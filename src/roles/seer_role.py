from .base_role import BaseRole


class SeerRole(BaseRole):
    def __init__(self):
        super().__init__("Seer")
        self.valid_ids = {}
        self.current_target = None
        self.current_target_role = None

    def handle_night_action(self, character_obj, public_info):
        player = character_obj.player
        role = character_obj.role
        alive_ids = public_info["alive_player_ids"]
        my_beliefs = player.beliefs
        targets = [
            pid for pid in alive_ids if pid != player.player_id 
            and (pid not in role.valid_ids)
        ]
        if not targets:
            return None
        wolf_prop = {id: my_beliefs[id]['Wolf'] for id in targets}
        target = max(wolf_prop, key=wolf_prop.get)
        self.current_target = target
        return target

    def handle_check_result(self, character_obj, target_id, is_good):
        player = character_obj.player
        # 1. 记录已查验名单，避免重复查验
        role_type = "Villager" if is_good else "Wolf" # 简单标记为好人或狼人
        self.valid_ids[target_id] = role_type
        
        # 2. 更新信念 (Beliefs)
        # 预言家对查验结果是 100% 确信的
        all_roles = player.beliefs[target_id].keys()
        new_probs = {r: 0.0 for r in all_roles}
        
        if is_good:
            # 如果是好人，平分概率给所有好人角色 (或者根据场上剩余配置细化，这里先简化)
            # 实际上预言家只能知道“非狼”，不能区分平民和神
            good_roles = [r for r in all_roles if r != "Wolf"]
            prob = 1.0 / len(good_roles) if good_roles else 0
            for r in good_roles:
                new_probs[r] = prob
        else:
            # 如果是狼人，Wolf 概率设为 1.0
            new_probs["Wolf"] = 1.0
            
        player.beliefs[target_id] = new_probs
        
    def handle_sheriff_selection(self, character_obj, public_info, private_info):
        pass

    def handle_day_action(self, character_obj, public_info, private_info):
        pass