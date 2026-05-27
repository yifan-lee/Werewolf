from .base import Role
from ..constants import RoleType, Faction

class Werewolf(Role):
    def __init__(self):
        super().__init__(RoleType.WEREWOLF, Faction.WEREWOLF, "狼人", priority=10)

    def perform_night_action(self, game_state, player):
        return player.act_night(game_state)
