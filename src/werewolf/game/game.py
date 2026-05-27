import random
from typing import List, Dict, Any, Optional
from ..constants import GamePhase, GameResult, Faction, WinCondition, RoleType
from ..player.player import Player

class Game:
    def __init__(self, players: List[Player], win_condition: WinCondition = WinCondition.KILL_SIDE):
        self.players = {p.player_id: p for p in players}
        self.alive_players = list(self.players.keys())
        self.day_count = 1
        self.phase = GamePhase.NIGHT
        self.sheriff_id: Optional[int] = None
        self.win_condition = win_condition
        self.logs = []
        self.winner: Optional[GameResult] = None
        
        # 记录每晚死亡的人，以便白天宣布
        self.night_deaths: List[int] = []

    def log(self, message: str):
        self.logs.append(f"[Day {self.day_count} - {self.phase.value}] {message}")

    def get_player(self, player_id: int) -> Optional[Player]:
        return self.players.get(player_id)

    def get_alive_players(self) -> List[Player]:
        return [self.players[pid] for pid in self.alive_players]

    def check_win_condition(self) -> bool:
        """检查游戏是否结束。如果结束，设置 self.winner 并返回 True"""
        alive = self.get_alive_players()
        werewolves = [p for p in alive if p.role.faction == Faction.WEREWOLF]
        villagers = [p for p in alive if p.role.faction == Faction.VILLAGER]
        gods = [p for p in alive if p.role.faction == Faction.GOD]

        if not werewolves:
            self.winner = GameResult.GOOD_WIN
            return True
            
        if self.win_condition == WinCondition.KILL_SIDE:
            if not villagers or not gods:
                self.winner = GameResult.WEREWOLF_WIN
                return True
        elif self.win_condition == WinCondition.KILL_ALL:
            if not villagers and not gods:
                self.winner = GameResult.WEREWOLF_WIN
                return True
                
        # 防死循环的极其罕见的平局判定（例如只剩1狼1猎人同时死亡）
        if not alive:
            self.winner = GameResult.DRAW
            return True

        return False

    def handle_death(self, player_id: int, is_night: bool = False, is_vote: bool = False):
        """处理玩家死亡，触发遗言、技能及移交警长"""
        if player_id not in self.alive_players:
            return
            
        player = self.players[player_id]
        self.alive_players.remove(player_id)
        player.is_alive = False
        self.log(f"玩家 {player_id} ({player.role.name}) 死亡。")

        # 1. 遗言环节 (首夜死亡或白天被票决)
        if (is_night and self.day_count == 1) or is_vote:
            last_words, claims = player.last_words_strategy(self)
            self.log(f"玩家 {player_id} 发表遗言: {last_words}")
            for p in self.get_alive_players():
                p.update_belief_after_last_words(player_id, last_words, claims, self)

        # 2. 移交警徽
        if self.sheriff_id == player_id:
            new_sheriff = player.transfer_sheriff_strategy(self)
            if new_sheriff in self.alive_players:
                self.sheriff_id = new_sheriff
                self.log(f"玩家 {player_id} 将警徽移交给了 玩家 {new_sheriff}。")
            else:
                self.sheriff_id = None
                self.log(f"玩家 {player_id} 撕毁了警徽。")

        # 3. 猎人开枪 (如果在夜晚是被毒死，通常不能开枪。这里简写，若需判定需由女巫毒杀传入特定标识)
        # 简单起见，默认可以开枪，复杂规则可通过添加 death_reason 完善
        if player.role.role_type == RoleType.HUNTER:
            # Note: 此处简化，如果需要“被毒不能开枪”，应在 night phase 记录死因
            target = player.act_night(self) # 借用 act_night 接口或专用接口，此处先用 act_night
            if target and target in self.alive_players:
                self.log(f"猎人 玩家 {player_id} 开枪带走了 玩家 {target}。")
                self.handle_death(target)

    def run_night_phase(self):
        self.phase = GamePhase.NIGHT
        self.log("天黑请闭眼。")
        self.night_deaths = []
        
        alive_players = self.get_alive_players()
        
        # 1. 狼人行动
        wolves = [p for p in alive_players if p.role.faction == Faction.WEREWOLF]
        wolf_targets = []
        for wolf in wolves:
            target = wolf.act_night(self)
            if target:
                wolf_targets.append(target)
                
        # 统一刀人目标 (简单策略：随机选一个狼人的目标，或投票最多的)
        wolf_kill = None
        if wolf_targets:
            wolf_kill = max(set(wolf_targets), key=wolf_targets.count)
            self.log(f"狼人阵营决定击杀 玩家 {wolf_kill}")

        # 2. 神职行动 (按优先级排序，预言家 > 女巫等)
        gods = [p for p in alive_players if p.role.faction == Faction.GOD]
        gods.sort(key=lambda x: x.role.priority, reverse=True)
        
        witch_save = False
        witch_poison = None

        for god in gods:
            if god.role.role_type == RoleType.SEER:
                # 预言家已经在 player 内部通过 act_night 获取信息了
                result = god.role.perform_night_action(self, god)
                god.receive_night_feedback(result)
            elif god.role.role_type == RoleType.WITCH:
                # 告知女巫狼人的刀人目标 (通过 game_state 给女巫提供接口或者约定)
                # 为了简单起见，我们把刀人信息暂存于一个字典传给女巫
                # 这里我们假设策略能通过 game_state 拿到信息，我们给 Game 临时加个属性
                self.current_wolf_kill = wolf_kill
                action = god.role.perform_night_action(self, god)
                god.receive_night_feedback(action)
                if action:
                    if action.get("save"):
                        witch_save = True
                        self.log(f"女巫使用了药，救了 玩家 {wolf_kill}")
                    elif "poison" in action:
                        witch_poison = action["poison"]
                        self.log(f"女巫使用了毒药，毒了 玩家 {witch_poison}")
                self.current_wolf_kill = None

        # 3. 结算死亡
        deaths = set()
        if wolf_kill and not witch_save:
            deaths.add(wolf_kill)
        if witch_poison:
            deaths.add(witch_poison)
            
        for d in deaths:
            self.night_deaths.append(d)
            # 夜间死亡统一在白天宣布并处理(调用 handle_death)
            
    def run_election_phase(self):
        self.phase = GamePhase.DAY_ELECTION
        self.log("开始竞选警长。")
        
        # 简单模拟：询问所有存活玩家是否上警及投票给谁
        votes = {} # candidate -> vote count
        candidates = []
        
        alive_players = self.get_alive_players()
        for p in alive_players:
            strategy_res = p.elect_sheriff_strategy(self)
            if strategy_res.get("run_for_sheriff"):
                candidates.append(p.player_id)
        
        if not candidates:
            self.log("无人竞选警长。")
            return
            
        self.log(f"竞选警长的玩家有: {candidates}")
        
        # 投票 (只有非竞选者能投票)
        for p in alive_players:
            if p.player_id not in candidates:
                strategy_res = p.elect_sheriff_strategy(self)
                vote = strategy_res.get("vote_for")
                if vote in candidates:
                    votes[vote] = votes.get(vote, 0) + 1
                    
        if votes:
            # 选出票数最多的
            winner = max(votes, key=votes.get)
            self.sheriff_id = winner
            self.log(f"玩家 {winner} 当选警长。")
        else:
            self.log("警长竞选流局。")

    def run_day_phase(self):
        self.phase = GamePhase.DAY_SPEECH
        self.log("天亮了。")
        
        # 宣布死者并处理遗言/技能
        if not self.night_deaths:
            self.log("昨夜是平安夜。")
        else:
            self.log(f"昨夜死亡的玩家是: {self.night_deaths}")
            for d in self.night_deaths:
                self.handle_death(d, is_night=True)
                
        if self.check_win_condition(): return
        
        # 发言环节
        alive_players = self.get_alive_players()
        # 发言顺序本应由警长决定，此处简单用从小到大
        for p in alive_players:
            speech, claims = p.speech_day_strategy(self)
            self.log(f"玩家 {p.player_id} 发言: {speech}")
            for other_p in self.get_alive_players():
                if other_p.player_id != p.player_id:
                    other_p.update_belief_after_speech(p.player_id, speech, claims, self)
                    
        # 投票环节
        self.phase = GamePhase.DAY_VOTE
        votes = {}
        for p in self.get_alive_players():
            target = p.vote_day_strategy(self)
            if target and target in self.alive_players:
                weight = 1.5 if self.sheriff_id == p.player_id else 1.0
                votes[target] = votes.get(target, 0) + weight
                
        if votes:
            exiled = max(votes, key=votes.get)
            exiled_player = self.players[exiled]
            
            # 白痴翻牌判定
            if exiled_player.role.role_type == RoleType.IDIOT and not exiled_player.is_idiot_revealed:
                exiled_player.is_idiot_revealed = True
                self.log(f"玩家 {exiled} 是白痴，翻牌免死，但失去投票权。")
                if self.sheriff_id == exiled:
                    self.sheriff_id = None # 通常翻牌后也会失去警徽，视规则而定
            else:
                self.log(f"玩家 {exiled} 被投票放逐。")
                self.handle_death(exiled, is_vote=True)
        else:
            self.log("所有人弃票，平安日。")

    def run(self) -> GameResult:
        """主循环"""
        self.log("游戏开始。")
        while not self.winner:
            self.run_night_phase()
            if self.check_win_condition(): break
            
            if self.day_count == 1:
                self.run_election_phase()
                
            self.run_day_phase()
            if self.check_win_condition(): break
            
            self.day_count += 1
            
        self.log(f"游戏结束，胜利方: {self.winner.value}")
        return self.winner
