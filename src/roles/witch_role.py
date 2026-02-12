from .base_role import BaseRole


class WitchRole(BaseRole):
    def __init__(self):
        super().__init__("Witch")
        self.used_poison = False
        self.used_heal = False

    def handle_night_action(self, character_obj, context):
        heal_target = None
        poison_target = None

        player = character_obj.player
        role = character_obj.role

        my_beliefs = player.beliefs

        if not role.used_heal:
            my_beliefs[context['wolves_target']]['Wolf']=0
            role.used_heal = True
            heal_target = context['wolves_target']
        elif not role.used_poison:
            alive_ids = context["alive_player_ids"]
            targets = [pid for pid in alive_ids if pid != player.player_id]
            wolf_prop = {id: player.beliefs[id]['Wolf'] for id in targets}
            poison_target = max(wolf_prop, key=wolf_prop.get)
            role.used_poison = True
        else:
            pass

        return heal_target, poison_target

    def handle_day_action(self, character_obj, context):
        pass