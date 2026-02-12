from .base_role import BaseRole


class SeerRole(BaseRole):
    def __init__(self):
        super().__init__("Seer")
        self.valid_ids = {}

    def handle_night_action(self, character_obj, context):
        player = character_obj.player
        role = character_obj.role
        alive_ids = context["alive_player_ids"]
        my_beliefs = player.beliefs
        targets = [
            pid for pid in alive_ids if pid != player.player_id 
            and (pid not in role.valid_ids)
        ]
        wolf_prop = {id: my_beliefs[id]['Wolf'] for id in targets}
        target = max(wolf_prop, key=wolf_prop.get)
        return target
        

    def handle_day_action(self, character_obj, context):
        pass