import random

from collections import Counter
from engine.player import Player
from engine.character import Character


class GameManager:
    def __init__(self):
        self.characters = []
        self.current_day = 0
        self.is_game_over = False
        self.winner = None
        # 定义角色池
        self.role_pool = ['Wolf']*4 + ['Villager']*4 + ['Seer', 'Witch', 'Hunter', 'Idiot']
        self.character_map = {}

    def setup_game(self):
        # random.shuffle(self.role_pool)
        for i, role_name in enumerate(self.role_pool):
            # 这里会实例化你之前定义的 Player 类
            player = Player(player_id=i)
            character = Character(role_name, player)
            self.characters.append(character)
            self.character_map[i] = character
        
        # 初始化的关键：注入“绝对认知”
        self._initialize_beliefs()

    def _initialize_beliefs(self):
        players_count = len(self.role_pool)
        all_role_counts = Counter(self.role_pool)
        for observer in self.characters:
            ob_player = observer.player
            for target in self.characters:
                tar_role_name = target.role_name
                tar_player = target.player
                if ob_player.player_id == tar_player.player_id:
                    # 对自己的认知：100% 确定
                    ob_player.beliefs[tar_player.player_id] = {role: (1.0 if role == observer.role_name else 0.0) for role in all_role_counts}
                    continue

                probs = {role: 0.0 for role in all_role_counts}
                if observer.role_name == 'Wolf':
                    if target.role_name == 'Wolf':
                        # 狼人认队友：100% 确定是狼
                        probs['Wolf'] = 1.0
                    else:
                        # 狼人看其他人：模糊处理（知道不是狼，但不知道具体是哪个好人）
                        good_role_count = players_count-all_role_counts['Wolf']
                        for role in all_role_counts:
                            if role == 'Wolf':
                                continue
                            probs[role] = all_role_counts[role]/good_role_count
                else:
                    # 好人看其他人：完全模糊（除了自己，剩下11个人都有可能是任何角色）
                    # 假设好人视角下的剩余人数分配
                    remaining_players_count = players_count-1
                    remaining_role_count = all_role_counts.copy()
                    remaining_role_count[observer.role_name] -= 1
                    for role in all_role_counts:
                        probs[role] = remaining_role_count[role]/remaining_players_count
                ob_player.beliefs[tar_player.player_id] = probs


    def run_simulation(self):
        while not self.check_game_over():
            self.current_day += 1
            self.night_phase()
            if self.check_game_over(): 
                break
            self.day_phase()
            if self.check_game_over(): 
                break


    

    def night_phase(self):
        print(f"--- 第 {self.current_day} 晚开始 ---")
        # 记录本晚发生的关键事件
        context = self.get_game_context()

        # 1. 狼人行动
        target_ids = []
        wolves = [c for c in self.characters if c.player.is_alive and c.role_name == "Wolf"]
        for wolf in wolves:
            target_id = wolf.role.handle_night_action(wolf, context)
            target_ids.append(target_id)
        wolves_target = max(set(target_ids), key=target_ids.count)
        context['wolves_target'] = wolves_target

        # 2. 预言家行动
        seer = [c for c in self.characters if c.player.is_alive and c.role_name == "Seer"][0]
        seer_target = seer.role.handle_night_action(seer, context)
        context['seer_target'] = seer_target
        
        # 3. 女巫行动 (传入狼人目标，供女巫决策是否救人)
        witch = [c for c in self.characters if c.player.is_alive and c.role_name == "Witch"][0]
        witch_heal_target, witch_poison_target = witch.role.handle_night_action(witch, context)
        context['witch_heal_target'] = witch_heal_target
        context['witch_poison_target'] = witch_poison_target

        # 4. 夜晚结算 (处理最终谁死了)
        self.resolve_night_deaths(record)

    def get_game_context(self):
        return {
            "alive_player_ids": [c.player.player_id for c in self.characters if c.player.is_alive],
            "gold_water_claims": {c.player.player_id: c.player.gold_water_claims for c in self.characters if c.player.is_alive},
            "silver_water_claims": {c.player.player_id: c.player.silver_water_claims for c in self.characters if c.player.is_alive},
            "public_claims": {c.player.player_id: c.player.public_role_claim for c in self.characters},
            "sheriff_id": next((c.player.player_id for c in self.characters if c.player.is_sheriff), None),
            "current_day": self.current_day,
            # 这里还可以加入历史投票记录、已确认死亡名单等
        }




    def handle_wolf_kill(self):
        # 找到存活的狼人
        wolves = [p for p in self.players if p.is_alive and p.role_name == 'Wolf']
        if not wolves: return None

        # 找出所有非狼人作为潜在目标
        potential_targets = [p for p in self.players if p.is_alive and p.role_name != 'Wolf']
        

        def get_priority(target):
            # 注意：这里是基于“公开信息”的判断
            if target.public_role_claim == 'Seer': return 100
            if target.public_role_claim == 'Witch': return 80
            if target.public_role_claim in ['Hunter', 'Idiot']: return 60
            # 检查是否是金水（由任何存活的预言家宣称）
            if any(side == "Good" for side in target.gold_water_claims.values()):
                return 40
            return 10

        # 选取优先级最高的目标（如果有多个同级的，随机选一个）
        potential_targets.sort(key=get_priority, reverse=True)
        max_p = get_priority(potential_targets[0])
        final_list = [t for t in potential_targets if get_priority(t) == max_p]
        
        target = random.choice(final_list)
        return target.player_id


    def handle_seer_check(self):
        seer = next((p for p in self.players if p.is_alive and p.role_name == 'Seer'), None)
        if not seer: return None

        # 排除自己和已确认身份的目标
        # 策略：选择他信念中 Wolf 概率最高的非金水玩家
        others = [p for p in self.players if p.is_alive and p.player_id != seer.player_id]
        target = max(others, key=lambda p: seer.beliefs[p.player_id]['Wolf'])
        
        # 验证真实身份
        is_wolf = (self.players[target.player_id].role_name == 'Wolf')
        
        # 立即更新预言家的认知
        self.update_belief_after_check(seer, target.player_id, is_wolf)
        return target.player_id


    def handle_witch_action(self, record):
        witch = next((p for p in self.players if p.is_alive and p.role_name == 'Witch'), None)
        if not witch: return

        # 假设女巫类或属性中记录了药水状态：has_save = True, has_poison = True
        # 救人逻辑：如果被杀的是重要角色或自己，且有解药
        killed_id = record['wolf_kill_target']
        if killed_id is not None and witch.has_save:
            target_player = self.players[killed_id]
            # 策略：如果是神职、自己、或者已知好人，就救
            if target_player.role_name in ['Seer', 'Witch', 'Hunter'] or killed_id == witch.player_id:
                record['witch_used_save'] = True
                witch.has_save = False
                return # 用了救药通常当晚不建议开毒

        # 毒人逻辑：如果有毒药且没有救人
        if witch.has_poison:
            # 策略：选择一个他信念中 Wolf 概率极高的人（比如 > 0.8）
            potential_enemy = [p for p in self.players if p.is_alive and p.player_id != witch.player_id]
            target = max(potential_enemy, key=lambda p: witch.beliefs[p.player_id]['Wolf'])
            
            if witch.beliefs[target.player_id]['Wolf'] > 0.8: # 只有足够自信才开毒
                record['witch_used_poison'] = target.player_id
                witch.has_poison = False
        
    def resolve_night_deaths(self, record):
        deaths_tonight = []
        
        # 处理狼刀
        if record['wolf_kill_target'] is not None and not record['witch_used_save']:
            deaths_tonight.append(record['wolf_kill_target'])
        
        # 处理毒药
        if record['witch_used_poison'] is not None:
            deaths_tonight.append(record['witch_used_poison'])
            
        # 执行死亡逻辑
        for pid in set(deaths_tonight):
            self.players[pid].is_alive = False
            print(f"玩家 {pid} ({self.players[pid].role_name}) 在夜晚死亡。")

    
if __name__ == "__main__":
    game_manager = GameManager()
    game_manager.setup_game()

    print(game_manager.characters[8].role_name)
    print(game_manager.characters[8].player.beliefs[0])