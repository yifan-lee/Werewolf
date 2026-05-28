from werewolf.game.game import Game
from werewolf.player.player import Player
import random
from typing import Any, Dict, Tuple, List
from ..strategy import Strategy

class BasicStrategy(Strategy):
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
        if not targets:
            targets = [
                p.player_id for p in game_state.get_alive_players() if p.player_id != player.player_id
            ]
        scores = {pid: self.get_score(pid) for pid in targets}
        max_score = max(scores.values())
        top_targets = [pid for pid, s in scores.items() if s == max_score]
        return random.choice(top_targets) if top_targets else None

    def execute_death_effect(self, player: 'Player', game_state: Any) -> Any:
        # 默认没有特殊效果
        return None

    def transfer_sheriff_strategy(self, player: 'Player', game_state: Any) -> int:
        return self.vote_sheriff(player, game_state, None)

    def last_words_strategy(self, player: 'Player', game_state: 'Game') -> Tuple[str, Dict[str, Any]]:
        return "我是好人，我死得很冤。", {}

    def update_belief_after_last_words(self, player: 'Player', speaker_id: int, last_words: str, claims: Dict[str, Any], game_state: 'Game'):
        if not claims:
            return

        if speaker_id not in self.belief:
            self.belief[speaker_id] = {}
            
        role_claim = claims.get("jump_role")

        if role_claim:
            self.belief[speaker_id][f"is_{role_claim.lower()}"] = 1.0

        gold_water = claims.get("gold_water")
        if gold_water is not None:
            for target in claims.get("gold_water", []):
                if target not in self.belief:
                    self.belief[target] = {}
                self.belief[target]["is_gold_water"] = 1.0

        silver_water = claims.get("silver_water")
        if silver_water is not None:
            if silver_water not in self.belief:
                self.belief[silver_water] = {}
            self.belief[silver_water]["is_silver_water"] = 1.0

        check_kill = claims.get("check_kill")
        if check_kill is not None:
            if check_kill not in self.belief:
                self.belief[check_kill] = {}
            self.belief[check_kill]["is_werewolf"] = 1.0

    def speech_day_strategy(self, player: 'Player', game_state: 'Game') -> Tuple[str, Dict[str, Any]]:
        return f"我是好人，过。(来自 {player.role.name} 的随机发言)", {}


    def update_belief_after_speech(self, player: 'Player', speaker_id: int, speech: str, claims: Dict[str, Any], game_state: 'Game'):
        self.update_belief_after_last_words(player, speaker_id, speech, claims, game_state)

    def vote_day_strategy(self, player: 'Player', game_state: Any) -> int:
        alive_others = [
            p.player_id for p in game_state.get_alive_players() if p.player_id != player.player_id
        ]
        if not alive_others:
            return None
        scores = {pid: -self.get_score(pid) for pid in alive_others}
        max_score = max(scores.values())
        top_targets = [pid for pid, s in scores.items() if s == max_score]
        return random.choice(top_targets)

        

    ### Support functions

    def get_score(self, pid: int) -> float:
        b = self.belief.get(pid, {})
        score = 0.0
        # 优先级：预言家(1000) > 金水(800) > 女巫(600) > 银水(500) > 白痴(400) > 猎人(200) > 其他(0)
        if b.get("is_seer") == 1.0:
            score += 1000
        elif b.get("is_gold_water") == 1.0:
            score += 800
        elif b.get("is_witch") == 1.0:
            score += 600
        elif b.get("is_silver_water") == 1.0:
            score += 500
        elif b.get("is_idiot") == 1.0:
            score += 400
        elif b.get("is_hunter") == 1.0:
            score += 200
        elif b.get("is_werewolf") == 1.0:
            score -= 1000
        else:
            # 给一个基础分加上随机波动，确保其他好人之间随机杀
            score += random.random() * 10 
        return score