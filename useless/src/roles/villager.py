
from roles.role import Role
from config import RoleType

class Villager(Role):
    def __init__(self):
        super().__init__(RoleType.VILLAGER)
