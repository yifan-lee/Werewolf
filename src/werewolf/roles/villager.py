from .base import Role
from ..constants import RoleType, Faction

class Villager(Role):
    def __init__(self):
        super().__init__(RoleType.VILLAGER, Faction.VILLAGER, "平民", priority=0)

    def perform_night_action(self, game_state, player):
        return None
