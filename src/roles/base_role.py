class BaseRole:
    def __init__(self, role_name):
        self.role_name = role_name

    def handle_night_action(self, player_obj, context):
        """
        player_obj: 玩家实例，包含其 beliefs
        context: 包含 alive_players, public_claims, current_day 等
        返回: 决策结果（如目标 ID）
        """
        pass

    def handle_day_action(self, player_obj, context):
        """
        player_obj: 玩家实例，包含其 beliefs
        context: 包含 alive_players, public_claims, current_day 等
        返回: 决策结果（如目标 ID）
        """
        pass

    def handle_death_speech(self, character_obj, public_info, private_info):
        """
        character_obj: 自身角色对象
        public_info: 公共信息
        private_info: 私有信息
        返回: 某些角色可能返回 target_id (如猎人)
        """
        pass
        
    def handle_sheriff_transfer(self, character_obj, public_info, private_info):
        """
        character_obj: 自身角色对象
        public_info: 公共信息
        private_info: 私有信息
        返回: 新警长的 target_id
        """
        # 默认逻辑：好人传给最像好人的人
        player = character_obj.player
        alive_ids = public_info['alive_player_ids']
        
        # 排除自己
        targets = [pid for pid in alive_ids if pid != player.player_id]
        
        if not targets:
            return None
            
        # 找到最像好人（Wolf概率最低）的人
        wolf_prop = {pid: player.beliefs[pid].get('Wolf', 0) for pid in targets}
        target = min(wolf_prop, key=wolf_prop.get)
        
        return target

class VillagerRole(BaseRole):
    def __init__(self):
        super().__init__("Villager")

    def handle_night_action(self, player_obj, context):
        pass

    def handle_day_action(self, player_obj, context):
        pass