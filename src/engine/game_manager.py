import random

from collections import Counter
from collections import defaultdict
from engine.player import Player
from engine.character import Character


class GameManager:
    def __init__(self, verbose=True):
        self.verbose = verbose

        self.characters = []
        self.current_day = 0
        self.is_game_over = False
        self.winner = None
        # 定义角色池
        self.role_pool = ['Wolf']*4 + ['Villager']*4 + ['Seer', 'Witch', 'Hunter', 'Idiot']
        self.id_to_character = {}
        self.role_to_id = defaultdict(set)

        self.public_info = None
        self.private_info = defaultdict(dict)

    def setup_game(self):
        # random.shuffle(self.role_pool)
        for i, role_name in enumerate(self.role_pool):
            # 这里会实例化你之前定义的 Player 类
            player = Player(player_id=i)
            character = Character(role_name, player)
            self.characters.append(character)
            self.id_to_character[i] = character
            self.role_to_id[role_name].add(i)
        
        # 初始化的关键：注入“绝对认知”
        self._initialize_beliefs()
        self.public_info = self.get_game_public_info()

    def _initialize_beliefs(self):
        players_count = len(self.role_pool)
        all_role_counts = Counter(self.role_pool)
        for observer in self.characters:
            ob_player = observer.player
            for target in self.characters:
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

    def get_game_public_info(self):
        return {
            "alive_player_ids": {c.player.player_id for c in self.characters if c.player.is_alive},
            "gold_water_claims": {c.player.player_id: c.player.gold_water_claims for c in self.characters if c.player.is_alive},
            "silver_water_claims": {c.player.player_id: c.player.silver_water_claims for c in self.characters if c.player.is_alive},
            "public_claims": {c.player.player_id: c.player.public_role_claim for c in self.characters},
            "sheriff_id": self.public_info['sheriff_id'] if self.public_info else None,
            "current_day": self.current_day,
            # 这里还可以加入历史投票记录、已确认死亡名单等
        }

    def run_simulation(self):
        while not self.check_game_over():
            self.night_phase()
            if self.check_game_over(): 
                break
            self.current_day += 1
            self.day_phase()
            if self.check_game_over(): 
                break


    def check_game_over(self):
        alive_ids = self.public_info['alive_player_ids']
        wolf_ids = self.role_to_id['Wolf']
        villager_ids = self.role_to_id['Villager']
        good_ids = set()
        for role, id in self.role_to_id.items():
            if (role != 'Wolf') and (role != 'Villager'):
                good_ids = good_ids.union(id)
        
        if not alive_ids.intersection(wolf_ids):
            self.winner = 'Villager'
            if self.verbose:
                print("所有狼人死亡，好人获胜")
            return(True)
        if not alive_ids.intersection(villager_ids):
            self.winner = 'Wolf'
            if self.verbose:
                print("所有平民死亡，狼人获胜")
            return(True)
        if not alive_ids.intersection(good_ids):
            self.winner = 'Wolf'
            if self.verbose:
                print("所有神职死亡，狼人获胜")
            return(True)
        return(False)

    def night_phase(self):
        if self.verbose:
            print(f"--- 第 {self.current_day} 晚开始 ---")

        # 1. 狼人行动
        if self.verbose:
            print(f"狼人请行动")
        target_ids = []
        wolves = [
            self.characters[id] for id in self.role_to_id['Wolf'] 
            if id in self.public_info['alive_player_ids']
        ]
        for wolf in wolves:
            target_id = wolf.role.handle_night_action(wolf, self.public_info)
            target_ids.append(target_id)
        wolves_target = max(set(target_ids), key=target_ids.count)
        self.private_info[self.current_day]['wolves_target'] = wolves_target
        if self.verbose:
            print(f"狼人选择杀害{wolves_target}号玩家")

        # 2. 预言家行动
        if self.verbose:
            print(f"预言家请行动")
        seer = next((c for c in self.characters if c.player.is_alive and c.role_name == "Seer"), None)
        if seer is None:
            seer_target = None
        else:
            seer_target = seer.role.handle_night_action(seer, self.public_info)
        self.private_info[self.current_day]['seer_target'] = seer_target
        if seer_target is not None:
            target_char = self.characters[seer_target]
            is_good = target_char.role_name != 'Wolf'
            seer.role.handle_check_result(seer, seer_target, is_good)
        if self.verbose:
            print(f"预言家选择查验{seer_target}号玩家")
        
        # 3. 女巫行动 (传入狼人目标，供女巫决策是否救人)
        if self.verbose:
            print(f"女巫请行动")
        witch = next((c for c in self.characters if c.player.is_alive and c.role_name == "Witch"), None)
        if witch is None:
            witch_heal_target = None
            witch_poison_target = None
        else:
            witch_heal_target, witch_poison_target = witch.role.handle_night_action(witch, self.public_info, self.private_info[self.current_day])
        self.private_info[self.current_day]['witch_heal_target'] = witch_heal_target
        self.private_info[self.current_day]['witch_poison_target'] = witch_poison_target
        if self.verbose:
            if witch_heal_target is not None:
                print(f"女巫选择救{witch_heal_target}号玩家")
            elif witch_poison_target is not None:
                print(f"女巫选择毒死{witch_poison_target}号玩家")
            else:
                print("女巫选择不救人也不毒死")

    

    def resolve_night_deaths(self):
        deaths_tonight = []
        
        # 处理狼刀
        if (
            (self.private_info[self.current_day-1]['wolves_target'] is not None) and 
            (not self.private_info[self.current_day-1]['witch_heal_target'])
        ):
            deaths_tonight.append(self.private_info[self.current_day-1]['wolves_target'])
        
        # 处理毒药
        if self.private_info[self.current_day-1]['witch_poison_target'] is not None:
            deaths_tonight.append(self.private_info[self.current_day-1]['witch_poison_target'])
            
        # 执行死亡逻辑
        for pid in set(deaths_tonight):
            self.id_to_character[pid].player.is_alive = False
            self.public_info['alive_player_ids'].remove(pid)
            if self.verbose:
                print(f"玩家{pid}在夜晚死亡。")
                
        self.public_info['deaths'] = list(set(deaths_tonight))
        return deaths_tonight

    def day_phase(self):
        
        if self.verbose:
            print(f"--- 第 {self.current_day} 天开始 ---")

        # 0. 选取警长
        if self.current_day == 1:
            if self.verbose:
                print(f"警长竞选开始")
            self.select_sheriff()
            # This line is problematic, as it assumes Seer[0] is the sheriff. The sheriff is set in select_sheriff.
        
        # 1. 结算前一晚的死亡
        self.resolve_night_deaths()

        # 2. 发表遗言
        self.death_speech()

        # 3. 移交警长
        self.transfer_sheriff()
        

        

        # 4. 公民议事
        self.public_discussion()

        # 5. 公民投票
        self.public_vote()

        # 6. 公民处决
        self.public_execution()



    def select_sheriff(self):
        # 1. 找到预言家并设为警长
        seer_ids = list(self.role_to_id['Seer'])
        if not seer_ids:
            if self.verbose:
                print("本局无预言家，无法选取警长")
            return

        seer_id = seer_ids[0]
        self.public_info['sheriff_id'] = seer_id
        
        if self.verbose:
            print(f"玩家 {seer_id} 当选警长 (预言家自动当选)")
            
        # 2. 更新全员认知：相信警长就是预言家
        for char in self.characters:
            player = char.player
            # 自己不用更新对自己身份的认知
            if player.player_id == seer_id:
                continue
            
            # 只有活着的玩家才需要更新认知(死人更新也没关系，但逻辑上是活人)
            # 这里简单处理，全员更新
            
            # 获取 Seer 在该玩家信念中的位置
            # 将 Seer 的概率设为 1.0，其他角色设为 0.0
            new_probs = {role: 0.0 for role in self.role_pool if role in player.beliefs[seer_id]}
            new_probs['Seer'] = 1.0
            player.beliefs[seer_id] = new_probs


    def death_speech(self):
        # 获取昨晚死亡的玩家
        # 注意：resolve_night_deaths 返回的是 deaths_tonight，但并没有保存到实例变量中供这里使用。
        # 我们需要在 resolve_night_deaths 中保存，或者在这里重新计算，或者传入。
        # 鉴于 resolve_night_deaths 已经修改了 is_alive，我们可以通过对比前一天的 alive_ids 和现在的来判断？
        # 或者最简单的方式：resolve_night_deaths 将死亡名单存入 self.private_info[self.current_day]['deaths']
        
        # 让我们先修改 resolve_night_deaths 保存死亡名单
        # (由于不能同时修改两个方法，我假设 resolve_night_deaths 已经保存了，或者我们需要在这里重新获取)
        # 重新获取比较麻烦。我们先假设有一个 self.current_deaths 变量或者从 private_info 获取。
        
        # 为了不破坏现有结构，我选择先修改 resolve_night_deaths (在下一个 tool call)，现在先写框架。
        # 假设 self.private_info[self.current_day]['deaths'] 存在。
        
        deaths = self.public_info.get('deaths', [])
        
        # 使用队列来处理链式死亡（如猎人带走的人又有遗言）
        # 但通常只有夜晚死的人才有遗言（猎人带走的人通常也有）
        # 简化处理：只处理昨晚死的，猎人带走的人立即处理其遗言
        
        processed_deaths = set()
        
        # 这是一个递归或者循环处理的过程
        death_queue = list(deaths)
        
        while death_queue:
            pid = death_queue.pop(0)
            if pid in processed_deaths:
                continue
            processed_deaths.add(pid)
            
            character = self.characters[pid]
            if not hasattr(character.role, 'handle_death_speech'):
                continue
                
            print(f"--- 玩家 {pid} ({character.role_name}) 发表遗言 ---")
            action = character.role.handle_death_speech(character, self.public_info, self.private_info[self.current_day])
            
            if action:
                if action['type'] == 'eliminate':
                    target_id = action['target']
                    if target_id in self.public_info['alive_player_ids']:
                        self.id_to_character[target_id].player.is_alive = False
                        self.public_info['alive_player_ids'].remove(target_id)
                        print(f"玩家 {target_id} 被带走死亡。")
                        death_queue.append(target_id)
                        
                elif action['type'] == 'publish_info':
                    # 预言家公布查验信息
                    valid_ids = action['data']
                    for char in self.characters:
                         # 更新所有好人（非狼）的认知
                        if char.player.player_id == pid: continue
                        if char.role_name == 'Wolf': continue
                        if not char.player.is_alive: continue
                        
                        for vid, role_type in valid_ids.items():
                            # 简单更新：如果是 Wolf，设为 1.0；如果是 Villager，设 Seer/Villager/etc 概率
                            # 简化：只更新 Wolf 概率
                            if role_type == 'Wolf':
                                char.player.beliefs[vid] = {r: (1.0 if r=='Wolf' else 0.0) for r in self.role_pool}
                            else:
                                # 如果是好人，则 Wolf 概率为 0
                                # 这里我们简单地把 Wolf 概率置零，并归一化其他概率（或者简单地不归一化，只修改 Wolf）
                                # 为了保持信念分布的合理性，最好是把 Wolf 的概率分配给其他角色
                                # 但最简单的做法是直接设为 0
                                char.player.beliefs[vid]['Wolf'] = 0.0
                                
                elif action['type'] == 'publish_silver_water':
                    # 女巫公布银水
                    target_id = action['target']
                    for char in self.characters:
                        if char.player.player_id == pid: continue
                        if char.role_name == 'Wolf': continue
                        
                        # 更新认知：该玩家不是狼
                        char.player.beliefs[target_id]['Wolf'] = 0.0

    def transfer_sheriff(self):
        sheriff_id = self.public_info['sheriff_id']
        # 检查警长是否存活
        if sheriff_id is None:
            return
            
        current_sheriff_char = self.characters[sheriff_id]
        if current_sheriff_char.player.is_alive:
            return
            
        print(f"警长 {sheriff_id} 已死亡，正在移交警徽...")
        
        # 调用警长的移交逻辑
        new_sheriff_id = current_sheriff_char.role.handle_sheriff_transfer(
            current_sheriff_char, 
            self.public_info, 
            self.private_info[self.current_day]
        )
        
        if new_sheriff_id is not None:
            self.public_info['sheriff_id'] = new_sheriff_id
            print(f"警徽移交给了 {new_sheriff_id}")
        else:
            print("警长撕毁了警徽 (未找到继承入)")
            self.public_info['sheriff_id'] = None


    
    def public_discussion(self):
        if self.verbose:
            print(f"--- 公民议事开始 ---")
            
        alive_ids = list(self.public_info['alive_player_ids'])
        # 可以随机顺序或者按座位号顺序发言，这里按座位号
        alive_ids.sort()
        
        for pid in alive_ids:
            character = self.characters[pid]
            action = character.role.handle_public_discussion(character, self.public_info, self.private_info[self.current_day])
            
            if action:
                if action['type'] == 'publish_info':
                    # 预言家公开发言
                    valid_ids = action['data']
                    for char in self.characters:
                        # 更新所有好人（非狼）的认知
                        if char.player.player_id == pid: continue
                        if char.role_name == 'Wolf': continue
                        if not char.player.is_alive: continue
                        
                        for vid, role_type in valid_ids.items():
                            if role_type == 'Wolf':
                                char.player.beliefs[vid] = {r: (1.0 if r=='Wolf' else 0.0) for r in self.role_pool}
                            else:
                                char.player.beliefs[vid]['Wolf'] = 0.0
                                
                elif action['type'] == 'publish_silver_water':
                    # 女巫公布银水
                    target_id = action['target']
                    for char in self.characters:
                        if char.player.player_id == pid: continue
                        if char.role_name == 'Wolf': continue
                        
                        # 更新认知：该玩家不是狼
                        char.player.beliefs[target_id]['Wolf'] = 0.0

    def public_vote(self):
        if self.verbose:
            print(f"--- 公民投票开始 ---")
            
        alive_ids = list(self.public_info['alive_player_ids'])
        votes = {} # voter_id -> target_id
        
        for pid in alive_ids:
            character = self.characters[pid]
            # 传入 public_info 和 private_info
            target_id = character.role.handle_public_vote(character, self.public_info, self.private_info[self.current_day])
            if target_id is not None:
                votes[pid] = target_id
                if self.verbose:
                    print(f"玩家 {pid} 投票给 {target_id}")
            else:
                if self.verbose:
                    print(f"玩家 {pid} 弃权")
                    
        # 统计票数
        if not votes:
            if self.verbose:
                print("无人投票，平安日")
            self.public_info['vote_result'] = None
            return
            
        vote_counts = Counter(votes.values())
        
        if self.verbose:
            print(f"投票结果: {vote_counts}")
            
        # 找到票数最多的
        max_votes = max(vote_counts.values())
        candidates = [pid for pid, count in vote_counts.items() if count == max_votes]
        
        if len(candidates) > 1:
            # 平票处理：简单起见，随机处决一个，或者（更规则的做法）进入PK发言，再次平票平安日。
            # 为了简化模拟，随机处决一个
            eliminated_id = random.choice(candidates)
            if self.verbose:
                print(f"平票 {candidates}，随机处决 {eliminated_id}")
        else:
            eliminated_id = candidates[0]
            if self.verbose:
                print(f"玩家 {eliminated_id} 被处决")
                
        self.public_info['vote_result'] = eliminated_id

    def public_execution(self):
        eliminated_id = self.public_info.get('vote_result')
        
        if eliminated_id is None:
            if self.verbose:
                print("无人被处决，进入黑夜")
            return
            
        print(f"--- 玩家 {eliminated_id} 被公投处决 ---")
        
        # 执行死亡
        self.id_to_character[eliminated_id].player.is_alive = False
        self.public_info['alive_player_ids'].remove(eliminated_id)
        
        # 处决遗言（通常被公投的人有遗言）
        character = self.characters[eliminated_id]
        if hasattr(character.role, 'handle_death_speech'):
            # 注意：这里的遗言处理逻辑与 death_speech 中的类似，但 death_speech 是处理昨晚死亡列表
            # 这里是处理单一死亡。
            # 为了复用逻辑，我们可以把 death_speech 的核心逻辑提取出来，或者在这里手动调用 handle_death_speech
            # 简单起见，这里直接调用，并处理返回的 action
            
            print(f"--- 玩家 {eliminated_id} ({character.role_name}) 发表遗言 ---")
            action = character.role.handle_death_speech(character, self.public_info, self.private_info[self.current_day])
            
            if action:
                if action['type'] == 'eliminate':
                    target_id = action['target']
                    if target_id in self.public_info['alive_player_ids']:
                        self.id_to_character[target_id].player.is_alive = False
                        self.public_info['alive_player_ids'].remove(target_id)
                        print(f"玩家 {target_id} 被带走死亡。")
                        
                        # 被带走的人也有遗言吗？
                        # 如果是猎人带走，被带走的人通常有遗言。
                        # 这里简略处理：递归调用比较麻烦，暂不处理被带走人的遗言
                        
                elif action['type'] == 'publish_info':
                    valid_ids = action['data']
                    for char in self.characters:
                        if char.player.player_id == eliminated_id: continue
                        if char.role_name == 'Wolf': continue
                        if not char.player.is_alive: continue
                        
                        for vid, role_type in valid_ids.items():
                            if role_type == 'Wolf':
                                char.player.beliefs[vid] = {r: (1.0 if r=='Wolf' else 0.0) for r in self.role_pool}
                            else:
                                char.player.beliefs[vid]['Wolf'] = 0.0
                                
                elif action['type'] == 'publish_silver_water':
                    # 女巫公布银水
                    target_id = action['target']
                    for char in self.characters:
                        if char.player.player_id == eliminated_id: continue
                        if char.role_name == 'Wolf': continue
                        
                        # 更新认知：该玩家不是狼
                        char.player.beliefs[target_id]['Wolf'] = 0.0
        
        # 处决后，如果警长死了，移交警徽
        if eliminated_id == self.public_info['sheriff_id']:
            self.transfer_sheriff()
    
if __name__ == "__main__":
    game = GameManager()
    game.setup_game()

    game.run_simulation()