
from src.config import RoleType
from src.roles.role import Role

class Player:
    def __init__(self, player_id: int, role: Role):
        self.id = player_id
        self.role = role
        self.is_alive = True
        self.sheriff = False
        
        # Status flags
        self.poisoned = False
        self.saved = False
        self.checked = False # By Seer
        
        # Memory/Knowledge (what this player knows)
        self.known_roles = {} # id -> RoleType (or "GOOD"/"BAD" if partial)
    
    def die(self):
        self.is_alive = False

    def revive(self):
        self.is_alive = True
        
    def __str__(self):
        status = "Alive" if self.is_alive else "Dead"
        sheriff = "[Sheriff]" if self.sheriff else ""
        return f"Player {self.id} ({self.role.name}) - {status} {sheriff}"
