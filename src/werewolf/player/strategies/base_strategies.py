from werewolf.game.game import Game
from werewolf.player.player import Player
import random
from typing import Any, Dict, Tuple, List
from ..strategy import Strategy

class BaseRandomStrategy(Strategy):
    """
    提供随机策略的基础实现，处理所有白天共用的投票、发言逻辑。
    夜晚逻辑 act_night 和复杂的 update_belief 由具体子类重写。
    """
    
    def __init__(self):
        super().__init__()
        # 简单概率矩阵：每个玩家维护对其他玩家阵营的信念
        # 例如: self.belief[player_id] = {"prob_good": 0.5, "prob_seer": 0.0}
        self.belief: Dict[int, Dict[str, float]] = {}

    def receive_night_feedback(self, player: 'Player', result: Any):
        # 基类不处理具体反馈
        pass

    def act_night(self, player: 'Player', game_state: 'Game') -> Any:
        return None

    def elect_sheriff_strategy(self, player: 'Player', game_state: 'Game') -> bool:
        # 默认不竞选警长
        return False

    def vote_sheriff(self, player: 'Player', game_state: 'Game', targets: List[int]) -> int:
        # 默认随机投票给警长候选人
        return random.choice(targets)

    def execute_death_effect(self, game_state: Any) -> Any:
        # 默认没有特殊效果
        return None

    def transfer_sheriff_strategy(self, game_state: Any) -> int:
        alive_players = [
            p.player_id for p in game_state.get_alive_players() 
        ]
        return random.choice(alive_players)

    def last_words_strategy(self, player: 'Player', game_state: 'Game') -> Tuple[str, Dict[str, Any]]:
        return "我是好人，我死得很冤。", {}

    def update_belief_after_last_words(self, player: 'Player', speaker_id: int, last_words: str, claims: Dict[str, Any], game_state: 'Game'):
        pass

    def speech_day_strategy(self, player: 'Player', game_state: 'Game') -> Tuple[str, Dict[str, Any]]:
        return f"我是好人，过。(来自 {player.role.name} 的随机发言)", {}


    def update_belief_after_speech(self, player: 'Player', speaker_id: int, speech: str, claims: Dict[str, Any], game_state: 'Game'):
        pass

    def vote_day_strategy(self, game_state: Any) -> int:
        alive_players = [
            p.player_id for p in game_state.get_alive_players() 
        ]
        return random.choice(alive_players)




    



    

    def vote_day_strategy(self, player: 'Player', game_state: 'Game') -> int:
        alive_others = [p.player_id for p in game_state.get_alive_players() if p.player_id != player.player_id]
        if alive_others:
            return random.choice(alive_others)
        return None

    def transfer_sheriff_strategy(self, player: 'Player', game_state: 'Game') -> int:
        alive_others = [p.player_id for p in game_state.get_alive_players() if p.player_id != player.player_id]
        if alive_others:
            return random.choice(alive_others)
        return None
