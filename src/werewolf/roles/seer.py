from .base import Role
from ..constants import RoleType, Faction

class Seer(Role):
    def __init__(self):
        super().__init__(RoleType.SEER, Faction.GOD, "预言家", priority=50)

    def perform_night_action(self, game_state, player):
        target_id = player.act_night(game_state)
        if target_id is not None:
            target_player = game_state.get_player(target_id)
            if target_player:
                is_werewolf = target_player.role.faction == Faction.WEREWOLF
                return {"target": target_id, "is_werewolf": is_werewolf}
        return None
