
from src.roles.role import Role
from src.config import RoleType

class Hunter(Role):
    def __init__(self):
        super().__init__(RoleType.HUNTER)
