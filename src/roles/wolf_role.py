from .base_role import BaseRole

import random

class WolfRole(BaseRole):
    def __init__(self):
        super().__init__("Wolf")

    def handle_night_action(self, character_obj, context):
        player = character_obj.player
        alive_ids = context["alive_player_ids"]
        my_beliefs = player.beliefs
        targets = [
            pid for pid in alive_ids if pid != player.player_id 
            and my_beliefs.get(pid, {}).get("Wolf", 0) < 1
        ]
        for pid in targets:
            if my_beliefs.get(pid, {}).get("Seer", 0) >= 1.0:
                return pid
        for pid in targets:
            if my_beliefs.get(pid, {}).get("Witch", 0) >= 1.0:
                return pid
        for pid in targets:
            if my_beliefs.get(pid, {}).get("Hunter", 0) >= 1.0:
                return pid
        for pid in targets:
            if my_beliefs.get(pid, {}).get("Idiot", 0) >= 1.0:
                return pid
        for pid in targets:
            if context['gold_water_claims'].get(pid, {}):
                return pid
        for pid in targets:
            if context['silver_water_claims'].get(pid, {}):
                return pid
        return random.choice(targets) if targets else None
        
        

    def handle_day_action(self, character_obj, context):
        pass