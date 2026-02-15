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

    def handle_sheriff_transfer(self, character_obj, public_info, private_info):
        # 狼人优先传给狼队友
        player = character_obj.player
        alive_ids = public_info['alive_player_ids']
        
        # 排除自己
        targets = [pid for pid in alive_ids if pid != player.player_id]
        
        if not targets:
            return None
            
        # 优先传给狼队友 (在 beliefs 中 Wolf=1.0 的)
        team_mates = [pid for pid in targets if player.beliefs[pid].get('Wolf', 0) == 1.0]
        
        if team_mates:
            return random.choice(team_mates)
            
        # 如果没有队友（只剩自己），随机传给一个人（或者传给最像好人的装好人？）
        # 简单起见，随机传
        return random.choice(targets)

    def handle_public_vote(self, character_obj, public_info, private_info):
        # 狼人投给对狼人威胁最大的人，或者为了混淆视听投给被公投的人？
        # 用户要求：和杀人逻辑一样 (即 handle_night_action)
        return self.handle_night_action(character_obj, public_info)