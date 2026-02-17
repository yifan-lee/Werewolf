
from typing import Dict, TYPE_CHECKING, List, Optional
from roles.role import Role
from config import RoleType

if TYPE_CHECKING:
    from player import Player

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
            
        # Select target with highest kill score
        best_target = max(potential_targets, key=lambda t: self.calculate_kill_score(t, knowledge_prob))
        return best_target

    def choose_successor(self, game: 'WerewolfGame', alive_players: List['Player'], knowledge_prob: Dict[int, Dict[RoleType, float]]) -> 'Player':
        # Werewolf chooses a teammate
        import random
        teammates = [p for p in alive_players if p.role.role_type == RoleType.WEREWOLF]
        if teammates:
            return random.choice(teammates)
            
        return super().choose_successor(game, alive_players, knowledge_prob)

    ## 假装一下好人，按照好人的方式投票
    # def vote(self, game: 'WerewolfGame', alive_players: List['Player'], knowledge_prob: Dict[int, Dict[RoleType, float]]) -> Optional['Player']:
    #     # Werewolf voting logic is same as kill target (strategic)
    #     return self.choose_kill_target(alive_players, knowledge_prob)
