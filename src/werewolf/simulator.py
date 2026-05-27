import multiprocessing
from typing import List, Type, Dict
from .player.strategy import Strategy
from .player.player import Player
from .game.game import Game
from .constants import GameResult, WinCondition

class GameConfig:
    def __init__(self, 
                 roles_setup: List['Role'], 
                 strategy_class: Type[Strategy], 
                 win_condition: WinCondition = WinCondition.KILL_SIDE):
        """
        :param roles_setup: 角色实例列表，比如 [Werewolf(), Werewolf(), Villager(), Seer() ...]
        :param strategy_class: 将会实例化并分配给每一个玩家的策略类 (也可以改为每个座位不同策略)
        :param win_condition: 胜利条件
        """
        self.roles_setup = roles_setup
        self.strategy_class = strategy_class
        self.win_condition = win_condition
        self.num_players = len(roles_setup)

    def create_players(self) -> List[Player]:
        players = []
        for i, role in enumerate(self.roles_setup):
            # 座位号从 1 开始
            player_id = i + 1
            strategy = self.strategy_class()
            player = Player(player_id, role, strategy)
            players.append(player)
        return players


class Simulator:
    def __init__(self, config: GameConfig, num_games: int):
        self.config = config
        self.num_games = num_games
        self.results = {
            GameResult.WEREWOLF_WIN: 0,
            GameResult.GOOD_WIN: 0,
            GameResult.DRAW: 0
        }

    def _run_single_game(self, seed: int) -> GameResult:
        import random
        random.seed(seed)
        players = self.config.create_players()
        # 打乱座位 (如果需要的话，当前是顺序排列角色然后绑定ID，打乱角色更合理)
        roles = [p.role for p in players]
        random.shuffle(roles)
        for i, p in enumerate(players):
            p.role = roles[i]
            
        game = Game(players, self.config.win_condition)
        result = game.run()
        return result

    def run(self, parallel: bool = True):
        print(f"开始模拟 {self.num_games} 局游戏...")
        if parallel:
            with multiprocessing.Pool() as pool:
                # 传入不同的 seed 保证随机性
                results = pool.map(self._run_single_game, range(self.num_games))
            for res in results:
                self.results[res] += 1
        else:
            for i in range(self.num_games):
                res = self._run_single_game(i)
                self.results[res] += 1
                
        self.print_statistics()

    def print_statistics(self):
        print("\n=== 模拟结果统计 ===")
        print(f"总局数: {self.num_games}")
        print(f"狼人胜率: {self.results[GameResult.WEREWOLF_WIN] / self.num_games * 100:.2f}%")
        print(f"好人胜率: {self.results[GameResult.GOOD_WIN] / self.num_games * 100:.2f}%")
        print(f"平局率: {self.results[GameResult.DRAW] / self.num_games * 100:.2f}%")
