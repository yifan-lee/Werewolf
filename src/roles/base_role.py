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
        
    def handle_public_discussion(self, character_obj, public_info, private_info):
        """
        公开发言阶段，角色可以公布信息。
        返回: dict 或 None
        """
        return None

    def handle_public_vote(self, character_obj, public_info, private_info):
        """
        公开投票阶段。
        返回: target_id
        """
        # 默认逻辑（好人）：投给最像狼的人
        player = character_obj.player
        alive_ids = public_info['alive_player_ids']
        
        # 排除自己
        targets = [pid for pid in alive_ids if pid != player.player_id]
        
        if not targets:
            return None
            
        # 找到最像狼（Wolf概率最高）的人
        wolf_prop = {pid: player.beliefs[pid].get('Wolf', 0) for pid in targets}
        # 如果所有人的 Wolf 概率都是 0 (比如初始状态)，随机投吗？或者不投？
        # python max on empty sequence errors, but we checked targets.
        # 如果 probabilities 都是一样的，max 会返回第一个。
        target = max(wolf_prop, key=wolf_prop.get)
        
        return target

class VillagerRole(BaseRole):
    def __init__(self):
        super().__init__("Villager")

    def handle_night_action(self, player_obj, context):
        pass

    def handle_day_action(self, player_obj, context):
        pass