from .base import Role
from ..constants import RoleType, Faction

class Idiot(Role):
    def __init__(self):
        super().__init__(RoleType.IDIOT, Faction.GOD, "白痴", priority=0)

    def perform_night_action(self, game_state, player):
        return None
