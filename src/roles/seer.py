

from typing import List, Dict, TYPE_CHECKING
from roles.role import Role
from config import RoleType

if TYPE_CHECKING:
    from player import Player

class Seer(Role):
    def __init__(self):
        super().__init__(RoleType.SEER)
        self.checked_players = [] # List of player IDs in order of check
        self.sheriff_candidacy_prob = 1.0

    def choose_check_target(self, alive_players: List['Player'], knowledge_prob: Dict[int, Dict[RoleType, float]]) -> 'Player':
        # Filter checked players
        checked_ids = set(self.checked_players)
        candidates = [p for p in alive_players if p.role.role_type != RoleType.SEER and p.id not in checked_ids]
        
        if not candidates:
            return None
            
        # Prioritize highest Wolf probability
        best_target = None
        max_wolf_prob = -1.0
        
        for p in candidates:
            probs = knowledge_prob.get(p.id, {})
            wolf_prob = probs.get(RoleType.WEREWOLF, 0.0)
            
            # Simple tie-breaking: first one found (or could use random if tie)
            if wolf_prob > max_wolf_prob:
                max_wolf_prob = wolf_prob
                best_target = p
        
        return best_target

    def share_information(self, my_player: 'Player', all_players: List['Player']):
        from utils import logger
        
        # Share knowledge about confirmed roles (1.0 probability)
        for pid, probs in my_player.knowledge_prob.items():
            # Check for 1.0 probability (certainty)
            known_role = next((r for r, p in probs.items() if p >= 0.99), None)
            if not known_role: continue
            
            status_str = known_role.value
            logger.info(f"[Discussion] Seer {my_player.id} says: Player {pid} is {status_str}")
            
            if known_role == RoleType.WEREWOLF:
                # 1. If Wolf, everyone marks them as Wolf certain
                for p in all_players:
                    p.mark_role_certain(pid, RoleType.WEREWOLF)
                    
            elif known_role == RoleType.VILLAGER: # Represents "Good"
                # 2. If Good, everyone rules out Wolf
                for p in all_players:
                    p.rule_out_role(pid, RoleType.WEREWOLF)
                    if p.id == pid:
                        p.is_gold_water = True
                        
        # Also reveal self as Seer to everyone (trust me, I'm Seer)
        # In this simplified logic, we assume people believe them.
        for p in all_players:
            p.mark_role_certain(my_player.id, RoleType.SEER)


    def choose_successor(self, alive_players: List['Player'], knowledge_prob: Dict[int, Dict[RoleType, float]]) -> 'Player':
        # Seer chooses a known Good player (Gold Water)
        import random
        
        known_good = []
        for p in alive_players:
            probs = knowledge_prob.get(p.id, {})
            # Check if likely good (Villager or God roles having high prob, excluding Werewolf)
            # Simplified: Check if Wolf prob is low or verified Good
            wolf_prob = probs.get(RoleType.WEREWOLF, 0.0)
            if wolf_prob < 0.01 and any(v > 0.9 for k, v in probs.items() if k != RoleType.WEREWOLF):
                known_good.append(p)
                
        if known_good:
            return random.choice(known_good)
            
        return super().choose_successor(alive_players, knowledge_prob)
