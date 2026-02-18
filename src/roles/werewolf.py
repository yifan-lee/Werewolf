
from typing import Dict, TYPE_CHECKING, List, Optional
from roles.role import Role
from config import RoleType
import random

if TYPE_CHECKING:
    from player import Player
    from game import WerewolfGame


class Werewolf(Role):
    def __init__(self):
        super().__init__(RoleType.WEREWOLF)

    def calculate_kill_score(self, target: 'Player', knowledge_prob: Dict[int, Dict[RoleType, float]]) -> float:
        score = 0
        probs = knowledge_prob.get(target.id, {})
        
        # 1. Seer (High Priority)
        score += probs.get(RoleType.SEER, 0) * 1000
        # 2. Witch
        score += probs.get(RoleType.WITCH, 0) * 800
        # 3. God (Hunter/Idiot)
        score += probs.get(RoleType.HUNTER, 0) * 500
        score += probs.get(RoleType.IDIOT, 0) * 500
        
        # 4. Silver Water (Saved by witch)
        if target.saved:
            score += 200
            
        # 5. Gold Water (Confirmed Good by Seer - visible reveal)
        if target.is_gold_water:
            score += 300
        
        # 6. Sheriff
        if target.sheriff:
            score += 100
            
        # 7. Other Good (Villager) -- implicitly lower score if probs are low for gods
        
        return score

    def choose_kill_target(self, alive_players: List['Player'], knowledge_prob: Dict[int, Dict[RoleType, float]]) -> Optional['Player']:
        potential_targets = [p for p in alive_players if p.role.role_type != RoleType.WEREWOLF]
        if not potential_targets:
            return None
            
        # Select target with highest kill score (random among ties)
        max_score = -1.0
        best_targets = []
        
        for p in potential_targets:
            score = self.calculate_kill_score(p, knowledge_prob)
            if score > max_score:
                max_score = score
                best_targets = [p]
            elif score == max_score:
                best_targets.append(p)
                
        if not best_targets:
            return None
            
        return random.choice(best_targets)

    def choose_successor(self, game: 'WerewolfGame', alive_players: List['Player'], knowledge_prob: Dict[int, Dict[RoleType, float]]) -> 'Player':
        # Werewolf chooses a teammate
        teammates = [p for p in alive_players if p.role.role_type == RoleType.WEREWOLF]
        if teammates:
            return random.choice(teammates)
            
        return super().choose_successor(game, alive_players, knowledge_prob)

    # ## 假装一下好人，按照好人的方式投票
    # def vote(self, game: 'WerewolfGame', alive_players: List['Player'], knowledge_prob: Dict[int, Dict[RoleType, float]], my_player: 'Player', leader_suggestion: Optional['Player'] = None) -> Optional['Player']:
    #     # Werewolf voting logic is same as kill target (strategic)
    #     return self.choose_kill_target(alive_players, knowledge_prob)
