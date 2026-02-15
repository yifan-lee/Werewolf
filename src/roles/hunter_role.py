from .base_role import BaseRole


class HunterRole(BaseRole):
    def __init__(self):
        super().__init__("Hunter")

    def handle_night_action(self, player_obj, context):
        # 逻辑：查看 context 中的 alive_players
        # 结合 player_obj.beliefs 找到最像预言家或女巫的人
        pass

    def handle_day_action(self, player_obj, context):
        pass

    def handle_death_speech(self, character_obj, public_info, private_info):
        # 猎人死后开枪带走一人
        player = character_obj.player
        alive_ids = public_info['alive_player_ids']
        
        # 排除自己
        targets = [pid for pid in alive_ids if pid != player.player_id]
        
        if not targets:
            return None
            
        # 找到最像狼的人
        wolf_prop = {pid: player.beliefs[pid].get('Wolf', 0) for pid in targets}
        target = max(wolf_prop, key=wolf_prop.get)
        
        print(f"猎人 {player.player_id} 发动技能，带走了 {target}")
        return {"type": "eliminate", "target": target}