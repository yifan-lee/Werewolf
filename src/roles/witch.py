
from typing import TYPE_CHECKING, List, Dict, Optional
from roles.role import Role
from config import RoleType

if TYPE_CHECKING:
    from player import Player

class Witch(Role):
    def __init__(self):
        super().__init__(RoleType.WITCH)
        self.has_antidote = True
        self.has_poison = True
        self.sheriff_candidacy_prob = 1.0
        
    def use_antidote(self):
        if self.has_antidote:
            self.has_antidote = False
            return True
        return False
        
    def use_poison(self):
        if self.has_poison:
            self.has_poison = False
            return True
        return False

    def choose_save_decision(self, night_kill: 'Player', knowledge_prob: Dict[int, Dict[RoleType, float]]) -> bool:
        """
        Decide whether to save the night kill target.
        """
        if not self.has_antidote:
            return False
            
        # Heuristic: Save if not self (or allow self save setting)
        # Prompt says "默认救" (Default save).
        return True

    def choose_poison_target(self, alive_players: List['Player'], knowledge_prob: Dict[int, Dict[RoleType, float]]) -> Optional['Player']:
        """
        Decide whether to poison someone and whom.
        """
        if not self.has_poison:
            return None
            
        # Find most suspicious target > 25% wolf prob
        potential_targets = [p for p in alive_players] 
        
        best_target = None
        max_wolf_prob = 0.0
        
        for p in potential_targets:
            probs = knowledge_prob.get(p.id, {})
            wolf_prob = probs.get(RoleType.WEREWOLF, 0.0)
            if wolf_prob > max_wolf_prob:
                max_wolf_prob = wolf_prob
                best_target = p
        
        if best_target and max_wolf_prob > 0.25:
             return best_target
             
        return None
        if best_target and max_wolf_prob > 0.25:
             return best_target
             
        return None

    def share_information(self, my_player: 'Player', all_players: List['Player']):
        # Witch can share if they saved someone (Silver Water)
        # But we need to know WHO they saved. 
        # Currently, 'saved' status is on the player.
        # Witch doesn't store history internally in this simplified model, 
        # but we can check if any player is 'saved' and maybe Witch claims it?
        # A bit tricky if multiple witches (unlikely) or if we want to confirm IT WAS ME.
        # Simplified: If there is a saved player, Witch claims standard silver water.
        
        from utils import logger
        
        # Check for self-knowledge or inferred from game state?
        # Actually, in run_night, we set p.saved = True.
        # But we don't know if *I* saved them technically unless we track it.
        # Let's assume singular Witch for now or iterate players.
        
        # Better approach: Witch should probably remember who they saved?
        # But for strictly following the prompt "most pass, only witch and seer update others"
        # Let's verify standard logic: Witch sees someone saved, claims credit.
        
        for p in all_players:
            if p.saved:
                 logger.info(f"[Discussion] Witch {my_player.id} says: I saved Player {p.id} last night! (Silver Water)")
                 
                 # Everyone rules out Wolf for Silver Water
                 for listener in all_players:
                     listener.rule_out_role(p.id, RoleType.WEREWOLF)

        # Reveal self as Witch
        for p in all_players:
            p.mark_role_certain(my_player.id, RoleType.WITCH)

    def choose_successor(self, alive_players: List['Player'], knowledge_prob: Dict[int, Dict[RoleType, float]]) -> 'Player':
        # Witch chooses the player she saved (Silver Water) if alive
        for p in alive_players:
            if p.saved: # Assuming p.saved checks the flag
                return p
        
        return super().choose_successor(alive_players, knowledge_prob)

