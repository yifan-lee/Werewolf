
from src.roles.role import Role
from src.config import RoleType

class Witch(Role):
    def __init__(self):
        super().__init__(RoleType.WITCH)
        self.has_antidote = True
        self.has_poison = True
        
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
