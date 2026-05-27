from typing import Dict, List, TYPE_CHECKING
from config import RoleType
from roles.role import Role

class Player:
    def __init__(self, player_id: int, role: Role):
        self.id = player_id
        self.role = role
        self.is_alive = True
        self.sheriff = False
        
        # Status flags
        self.status = {} # TBD: generalized status
        self.poisoned = False
        self.saved = False
        self.is_gold_water = False # Confirmed good by Seer publicly
        
        # Memory/Knowledge
        self.knowledge_prob: Dict[int, Dict[RoleType, float]] = {} # id -> {Role: Prob}
    
    def die(self):
        self.is_alive = False

    def revive(self):
        self.is_alive = True
        
    def __str__(self):
        status = "Alive" if self.is_alive else "Dead"
        sheriff = "[Sheriff]" if self.sheriff else ""
        return f"Player {self.id} ({self.role.name}) - {status} {sheriff}"

    def initialize_knowledge(self, players: List['Player'], config: Dict):
        """
        Initialize knowledge about other players based on own role and game config.
        """
        my_role = self.role.role_type
        
        # Helper to calculate probs for unknown pool
        def calc_probs(subset_roles: List[RoleType]):
            counts = {}
            for r in subset_roles:
                counts[r] = counts.get(r, 0) + 1
            total = len(subset_roles)
            return {r: cnt/total for r, cnt in counts.items()}

        if my_role == RoleType.WEREWOLF:
            # Wolves know teammates
            teammates = [p for p in players if p.role.role_type == RoleType.WEREWOLF and p != self]
            teammate_ids = {t.id for t in teammates}
            
            # Unknown pool: All players - Me - Teammates
            # The roles in this pool are exactly the non-wolf roles from config
            unknown_roles_pool = []
            for role_type, count in config["role_counts"].items():
                if role_type == RoleType.WEREWOLF: continue 
                unknown_roles_pool.extend([role_type] * count)
            
            probs = calc_probs(unknown_roles_pool)
            
            for target in players:
                if target == self: continue
                if target.id in teammate_ids:
                    self.knowledge_prob[target.id] = {RoleType.WEREWOLF: 1.0}
                else:
                    self.knowledge_prob[target.id] = probs.copy()

        else:
            # Good guy perspective
            # Knows only self.
            # Unknown pool = All roles - MyRole
            unknown_roles_pool = []
            # Add all roles first
            for role_type, count in config["role_counts"].items():
                unknown_roles_pool.extend([role_type] * count)
            # Remove my role once
            if my_role in unknown_roles_pool:
                unknown_roles_pool.remove(my_role)
            
            probs = calc_probs(unknown_roles_pool)
            
            for target in players:
                if target == self: continue
                self.knowledge_prob[target.id] = probs.copy()

    def mark_role_certain(self, target_id: int, role: RoleType):
        """
        Set target's role probability to 1.0 for the specified role, 0.0 for others.
        """
        if target_id not in self.knowledge_prob:
            return
        self.knowledge_prob[target_id] = {role: 1.0}

    def rule_out_role(self, target_id: int, role: RoleType):
        """
        Set target's specified role probability to 0.0.
        Redistribute the probability mass to other roles PROPORTIONALLY to their existing probability.
        """
        if target_id not in self.knowledge_prob:
            return
        
        probs = self.knowledge_prob[target_id]
        if role not in probs:
            return
            
        prob_to_distribute = probs[role]
        if prob_to_distribute == 0:
            return
            
        if prob_to_distribute >= 0.999:
            # If we are ruling out the ONLY possibility (contradiction), reset to empty or uniform?
            # Ideally shouldn't happen in valid logic logic. 
            # For now, just set to 0.
            probs[role] = 0.0
            return

        del probs[role]
        
        # Remaining mass
        current_total = sum(probs.values())
        if current_total > 0:
            # Redistribute proportionally
            # New value = Old value / current_total (which normalizes to 1.0)
            # Wait, we want to add prob_to_distribute back?
            # Actually, easiest way is to just normalize the remaining probabilities to sum to 1.
            # E.g. A=0.4, B=0.4, C=0.2. Rule out C. A=0.4/0.8=0.5, B=0.4/0.8=0.5.
            for r in probs:
                probs[r] = probs[r] / current_total
        else:
            # Use fall back if everything was 0? shouldn't happen
            pass
