from .base import Role
from ..constants import RoleType, Faction

class Hunter(Role):
    def __init__(self):
        super().__init__(RoleType.HUNTER, Faction.GOD, "猎人", priority=0)

    def perform_night_action(self, game_state, player):
        return None
