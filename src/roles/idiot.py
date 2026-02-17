
from src.roles.role import Role
from src.config import RoleType

class Idiot(Role):
    def __init__(self):
        super().__init__(RoleType.IDIOT)
        self.revealed = False
        
    def reveal(self):
        self.revealed = True
