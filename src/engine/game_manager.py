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
        self.role_to_id = defaultdict(list)
        self.sheriff_id = None

    def setup_game(self):
        # random.shuffle(self.role_pool)
        for i, role_name in enumerate(self.role_pool):
            # 这里会实例化你之前定义的 Player 类
            player = Player(player_id=i)
            character = Character(role_name, player)
            self.characters.append(character)
            self.id_to_character[i] = character
            self.role_to_id[role_name].append(i)
        
        # 初始化的关键：注入“绝对认知”
        self._initialize_beliefs()

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
        wolf_ids = self.role_to_id['Wolf']
        villager_ids = self.role_to_id['Villager']
        good_ids = []
        for role, id in self.role_to_id.items():
            if (role != 'Wolf') and (role != 'Villager'):
                good_ids.extend(id)
        
        if not any([self.id_to_character[wolf_id].player.is_alive for wolf_id in wolf_ids]):
            self.winner = 'Villager'
            if self.verbose:
                print("所有狼人死亡，好人获胜")
            return(True)
        if not any([self.id_to_character[villager_id].player.is_alive for villager_id in villager_ids]):
            self.winner = 'Wolf'
            if self.verbose:
                print("所有平民死亡，狼人获胜")
            return(True)
        if not any([self.id_to_character[good_id].player.is_alive for good_id in good_ids]):
            self.winner = 'Wolf'
            if self.verbose:
                print("所有神职死亡，狼人获胜")
            return(True)
        return(False)

    def night_phase(self):
        if self.verbose:
            print(f"--- 第 {self.current_day} 晚开始 ---")
        # 记录本晚发生的关键事件
        context = self.get_game_context()

        # 1. 狼人行动
        if self.verbose:
            print(f"狼人请行动")
        target_ids = []
        wolves = [c for c in self.characters if c.player.is_alive and c.role_name == "Wolf"]
        for wolf in wolves:
            target_id = wolf.role.handle_night_action(wolf, context)
            target_ids.append(target_id)
        wolves_target = max(set(target_ids), key=target_ids.count)
        context['wolves_target'] = wolves_target
        if self.verbose:
            print(f"狼人选择杀害{wolves_target}号玩家")

        # 2. 预言家行动
        if self.verbose:
            print(f"预言家请行动")
        seer = next((c for c in self.characters if c.player.is_alive and c.role_name == "Seer"), None)
        if seer is None:
            seer_target = None
        else:
            seer_target = seer.role.handle_night_action(seer, context)
        context['seer_target'] = seer_target
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
            witch_heal_target, witch_poison_target = witch.role.handle_night_action(witch, context)
        context['witch_heal_target'] = witch_heal_target
        context['witch_poison_target'] = witch_poison_target
        if self.verbose:
            if witch_heal_target is not None:
                print(f"女巫选择救{witch_heal_target}号玩家")
            elif witch_poison_target is not None:
                print(f"女巫选择毒死{witch_poison_target}号玩家")
            else:
                print("女巫选择不救人也不毒死")
        
        # # 4. 夜晚结算 (处理最终谁死了)
        # self.resolve_night_deaths(context)

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

    def resolve_night_deaths(self, context):
        deaths_tonight = []
        
        # 处理狼刀
        if context['wolves_target'] is not None and not context['witch_heal_target']:
            deaths_tonight.append(context['wolves_target'])
        
        # 处理毒药
        if context['witch_poison_target'] is not None:
            deaths_tonight.append(context['witch_poison_target'])
            
        # 执行死亡逻辑
        for pid in set(deaths_tonight):
            self.id_to_character[pid].player.is_alive = False
            if self.verbose:
                print(f"玩家{pid}在夜晚死亡。")
        return deaths_tonight

    def day_phase(self):
        if self.verbose:
            print(f"--- 第 {self.current_day} 天开始 ---")

        # 0. 选取警长
        if self.current_day == 1:
            if self.verbose:
                print(f"警长竞选开始")
            self.select_sheriff()
            self.sheriff_id = self.role_to_id['Seer'][0]
        
        # 1. 结算前一晚的死亡
        deaths_tonight = self.resolve_night_deaths(context)

        # 2. 移交警长
        if (self.sheriff_id is not None) and (self.sheriff_id in deaths_tonight):
            previous_sheriff = self.id_to_character[self.sheriff_id]
            new_sheriff_id = previous_sheriff.role.handle_sheriff_transfer(previous_sheriff, context)
            self.id_to_character[self.sheriff_id].player.is_sheriff = False
            self.id_to_character[new_sheriff_id].player.is_sheriff = True
            self.sheriff_id = new_sheriff_id
        

        

        # 1. 公民议事



        # 2. 公民投票



        # 3. 公民处决


    def select_sheriff(self):
        seer_id = self.role_to_id['Seer'][0]
        self.characters[seer_id].player.is_sheriff = True
    
if __name__ == "__main__":
    game_manager = GameManager()
    game_manager.setup_game()

    print(game_manager.characters[8].role_name)
    print(game_manager.characters[8].player.beliefs[0])