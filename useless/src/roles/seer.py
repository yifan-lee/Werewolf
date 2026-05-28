

from typing import List, Dict, TYPE_CHECKING, Optional
from roles.role import Role
from config import RoleType
import random
from utils import logger

if TYPE_CHECKING:
    from player import Player
    from game import WerewolfGame

class Seer(Role):
    def __init__(self):
        super().__init__(RoleType.SEER)
        self.checked_players = [] # List of player IDs in order of check
        self.sheriff_candidacy_prob = 1.0
        self.badge_flow_target: Optional[int] = None # Player ID

    def vote(self, game: 'WerewolfGame', alive_players: List['Player'], knowledge_prob: Dict[int, Dict[RoleType, float]], my_player: 'Player', leader_suggestion: Optional['Player'] = None) -> Optional['Player']:
        # Seer always votes for their most suspicious target (independent)
        best_targets = []
        max_wolf_prob = -1.0
        
        badge_flow_target_id = game.get_badge_flow_target()
        
        for p in alive_players:
             # Skip badge flow target if I am Good (Seer avoids voting for their own future check unless certain)
             # Actually, Seer checking someone doesn't mean they can't vote for them if they are already suspicious.
             # But let's keep consistency: if badge flow target logic applies generally.
             # However, Seer KNOWS who they checked.
             
             probs = knowledge_prob.get(p.id, {})
             wolf_prob = probs.get(RoleType.WEREWOLF, 0.0)
             
             if wolf_prob > max_wolf_prob:
                 max_wolf_prob = wolf_prob
                 best_targets = [p]
             elif wolf_prob == max_wolf_prob and max_wolf_prob >= 0:
                 best_targets.append(p)
                  
        if not best_targets:
            return None
            
        return random.choice(best_targets)

    def choose_check_target(self, alive_players: List['Player'], knowledge_prob: Dict[int, Dict[RoleType, float]]) -> 'Player':
        # If there's an announced badge flow target, try to check them first
        if self.badge_flow_target:
            target_p = next((p for p in alive_players if p.id == self.badge_flow_target), None)
            if target_p and target_p.id not in self.checked_players:
                return target_p

        # Filter checked players
        checked_ids = set(self.checked_players)
        candidates = [p for p in alive_players if p.role.role_type != RoleType.SEER and p.id not in checked_ids]
        
        if not candidates:
            return None
            
        # Prioritize highest Wolf probability (random among ties)
        best_targets = []
        max_wolf_prob = -1.0
        
        for p in candidates:
            probs = knowledge_prob.get(p.id, {})
            wolf_prob = probs.get(RoleType.WEREWOLF, 0.0)
            
            if wolf_prob > max_wolf_prob:
                max_wolf_prob = wolf_prob
                best_targets = [p]
            elif wolf_prob == max_wolf_prob and max_wolf_prob >= 0:
                best_targets.append(p)
        
        if not best_targets:
            return None
            
        
        return random.choice(best_targets)

    def share_information(self, my_player: 'Player', all_players: List['Player']):
        
        
        # 1. Share results of previous checks
        for pid, probs in my_player.knowledge_prob.items():
            known_role = next((r for r, p in probs.items() if p >= 0.99), None)
            if not known_role: continue
            
            status_str = known_role.value
            logger.info(f"[Discussion] Seer {my_player.id} says: Player {pid} is {status_str}")
            
            if known_role == RoleType.WEREWOLF:
                for p in all_players:
                    p.mark_role_certain(pid, RoleType.WEREWOLF)
            elif known_role == RoleType.VILLAGER:
                for p in all_players:
                    p.rule_out_role(pid, RoleType.WEREWOLF)
                    if p.id == pid:
                        p.is_gold_water = True
                        
        # 2. Badge Flow Announcement (Designating FUTURE target)
        if my_player.sheriff:
            # Pick a future target (someone not checked yet)
            checked_ids = set(self.checked_players)
            candidates = [p for p in all_players if p.is_alive and p.id != my_player.id and p.id not in checked_ids]
            
            if candidates:
                # Pick most suspicious for future check (random among ties)
                max_wolf_prob = max(my_player.knowledge_prob.get(p.id, {}).get(RoleType.WEREWOLF, 0.0) for p in candidates)
                top_candidates = [p for p in candidates if my_player.knowledge_prob.get(p.id, {}).get(RoleType.WEREWOLF, 0.0) == max_wolf_prob]
                
                self.badge_flow_target = random.choice(top_candidates).id
                logger.info(f"[Discussion] Seer {my_player.id} announces Badge Flow: Tonight will check Player {self.badge_flow_target}. If Good -> Transfer to them; If Wolf -> Transfer to previously known good.")

        # 3. Reveal self as Seer
        for p in all_players:
            p.mark_role_certain(my_player.id, RoleType.SEER)


    def choose_successor(self, game: 'WerewolfGame', alive_players: List['Player'], knowledge_prob: Dict[int, Dict[RoleType, float]]) -> 'Player':
        # Seer Badge Flow logic
        
        
        
        if self.badge_flow_target:
            target_id = self.badge_flow_target
            target_p = next((p for p in game.players if p.id == target_id), None)
            
            if target_p:
                probs = knowledge_prob.get(target_id, {})
                wolf_prob = probs.get(RoleType.WEREWOLF, 0.0)
                
                if wolf_prob < 0.01:
                    # Target is Good!
                    logger.info(f"Seer Badge Flow: Player {target_id} is Good. Transferring badge and revealing their role to all.")
                    # Update all players' knowledge
                    for p in game.players:
                        p.rule_out_role(target_id, RoleType.WEREWOLF)
                    
                    if target_p.is_alive:
                        return target_p
                else:
                    # Target is Wolf!
                    logger.info(f"Seer Badge Flow: Player {target_id} is Wolf. Revealing their role to all and transferring badge to known good.")
                    # Update all players' knowledge
                    for p in game.players:
                        p.mark_role_certain(target_id, RoleType.WEREWOLF)

        # Fallback: choose a known Good player (Gold Water)
        known_good = []
        for p in alive_players:
            probs = knowledge_prob.get(p.id, {})
            wolf_prob = probs.get(RoleType.WEREWOLF, 0.0)
            if wolf_prob < 0.01 and any(v > 0.9 for k, v in probs.items() if k != RoleType.WEREWOLF):
                known_good.append(p)
                
        if known_good:
            return random.choice(known_good)
            
        return super().choose_successor(game, alive_players, knowledge_prob)
