from .base import Role
from ..constants import RoleType, Faction

class Witch(Role):
    def __init__(self):
        super().__init__(RoleType.WITCH, Faction.GOD, "女巫", priority=30)
        self.has_antidote = True
        self.has_poison = True

    def perform_night_action(self, game_state, player):
        action = player.act_night(game_state)
        if action:
            if action.get("save") and self.has_antidote:
                self.has_antidote = False
                return {"save": True}
            elif "poison" in action and self.has_poison:
                self.has_poison = False
                return {"poison": action["poison"]}
        return None
