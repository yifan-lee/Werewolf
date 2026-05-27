from werewolf.game.game import Game
from werewolf.player.player import Player
import random
from typing import Any, Dict, List
from .base_strategies import BaseRandomStrategy
from ...constants import Faction

class WerewolfBaselineStrategy(BaseRandomStrategy):

    def act_night(self, player: 'Player', game_state: 'Game') -> Any:
        alive_non_wolves = [
            p.player_id for p in game_state.get_alive_players() 
            if p.role.faction != Faction.WEREWOLF
        ]
        
        if not alive_non_wolves:
            return None
            
        def get_kill_score(pid: int) -> float:
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
            else:
                # 给一个基础分加上随机波动，确保其他好人之间随机杀
                score += random.random() * 10 
            return score
            
        scores = {pid: get_kill_score(pid) for pid in alive_non_wolves}
        max_score = max(scores.values())
        top_targets = [pid for pid, s in scores.items() if s == max_score]
        
        return random.choice(top_targets) if top_targets else random.choice(alive_non_wolves)

    def elect_sheriff_strategy(self, player: 'Player', game_state: 'Game') -> bool:
        return False

    def vote_sheriff(self, player: 'Player', game_state: 'Game', targets: List['Player']):
        def get_kill_score(pid: int) -> float:
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
            else:
                # 给一个基础分加上随机波动，确保其他好人之间随机杀
                score += random.random() * 10 
            return score
            
        scores = {pid: get_kill_score(pid) for pid in targets}
        max_score = max(scores.values())
        top_targets = [pid for pid, s in scores.items() if s == max_score]
        return random.choice(top_targets) if top_targets else random.choice(targets)

    def transfer_sheriff_strategy(self, player: 'Player', game_state: Any) -> Any:
        return self.act_night(player, game_state)

    

    def update_belief_after_speech(self, player: 'Player', speaker_id: int, speech: str, claims: Dict[str, Any], game_state: 'Game'):
        if not claims:
            return
            
        wolves = [p.player_id for p in game_state.get_alive_players() if p.role.faction == Faction.WEREWOLF]
        
        if speaker_id not in self.belief:
            self.belief[speaker_id] = {}
            
        role_claim = claims.get("jump_role")
        if role_claim == "Seer":
            # 检查预言家说的对不对
            is_correct = True
            has_info = False
            for target in claims.get("check_kill", []):
                has_info = True
                if target not in wolves:
                    is_correct = False
                    
            for target in claims.get("gold_water", []):
                has_info = True
                if target in wolves:
                    is_correct = False
            
            if has_info:
                if is_correct:
                    self.belief[speaker_id]["is_seer"] = 1.0
                    # 既然是真预言家，把他的金水也记下来
                    for target in claims.get("gold_water", []):
                        if target not in self.belief:
                            self.belief[target] = {}
                        self.belief[target]["is_gold_water"] = 1.0
                else:
                    self.belief[speaker_id]["is_seer"] = 0.0
        elif role_claim:
            # 跳其他身份
            self.belief[speaker_id][f"is_{role_claim.lower()}"] = 1.0
            
        silver_water = claims.get("silver_water")
        if silver_water is not None:
            if silver_water not in self.belief:
                self.belief[silver_water] = {}
            self.belief[silver_water]["is_silver_water"] = 1.0



# 以后这里可以加入:
# class WerewolfLLMStrategy(BaseLLMStrategy): ...
