from .base_role import BaseRole


class WitchRole(BaseRole):
    def __init__(self):
        super().__init__("Witch")
        self.used_poison = False
        self.used_heal = False
        self.heal_target_id = None

    def handle_night_action(self, character_obj, public_info, private_info_today):
        heal_target = None
        poison_target = None
        
        player = character_obj.player
        wolves_target = private_info_today.get('wolves_target')
        
        # 1. 判定是否使用解药
        if not self.used_heal and wolves_target is not None:
             # 这里可以加入策略：比如如果是自己被杀，或者关键人物被杀，就救
             # 目前策略：只要有药且有人死就救 (可以根据需要优化策略，比如第一晚必救)
            heal_target = wolves_target
            self.used_heal = True
            self.heal_target_id = heal_target # 记录被救玩家ID
            
            # 救人后更新认知：该玩家大概率是好人（也就是所谓的银水）
            # 注意：这里直接修改了 beliefs，可能需要更复杂的逻辑，比如仅仅标记为 "SilverWater"
            player.beliefs[heal_target]['Wolf'] = 0.0

        # 2. 判定是否使用毒药 (通常规则：一晚只能用一瓶药)
        # 如果当晚没用解药，且还有毒药，且有怀疑对象，则用毒
        if heal_target is None and not self.used_poison:
            alive_ids = public_info["alive_player_ids"]
            # 排除自己
            targets = [pid for pid in alive_ids if pid != player.player_id]
            
            # 找到最像狼的人
            wolf_prop = {pid: player.beliefs[pid].get('Wolf', 0) for pid in targets}
            
            if wolf_prop:
                most_suspicious_target = max(wolf_prop, key=wolf_prop.get)
                poison_target = most_suspicious_target
                self.used_poison = True

        return heal_target, poison_target

    def handle_death_speech(self, character_obj, public_info, private_info):
        # 如果女巫救过人，公布银水身份
        if self.used_heal and self.heal_target_id is not None:
            print(f"女巫 {character_obj.player.player_id} 发动技能，公布银水: {self.heal_target_id}")
            return {"type": "publish_silver_water", "target": self.heal_target_id}
        return None

    def handle_public_discussion(self, character_obj, public_info, private_info):
        # 如果女巫救过人，公布银水身份
        if self.used_heal and self.heal_target_id is not None:
            print(f"女巫 {character_obj.player.player_id} 公开发言，公布银水: {self.heal_target_id}")
            return {"type": "publish_silver_water", "target": self.heal_target_id}
        return None
             
    def handle_day_action(self, character_obj, context):
        pass