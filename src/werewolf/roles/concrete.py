from .base import Role
from ..constants import RoleType, Faction

class Werewolf(Role):
    def __init__(self):
        super().__init__(RoleType.WEREWOLF, Faction.WEREWOLF, "狼人", priority=10)

    def perform_night_action(self, game_state, player):
        # 狼人的行动通过 game_state 来统一结算，因为狼人是阵营行动（多只狼共同决定一个目标）
        # 这里只返回当前狼人想要杀的目标
        return player.act_night(game_state)


class Villager(Role):
    def __init__(self):
        super().__init__(RoleType.VILLAGER, Faction.VILLAGER, "平民", priority=0)

    def perform_night_action(self, game_state, player):
        # 平民夜晚无行动
        return None


class Seer(Role):
    def __init__(self):
        super().__init__(RoleType.SEER, Faction.GOD, "预言家", priority=20)

    def perform_night_action(self, game_state, player):
        # 预言家夜晚查验一个人的阵营
        target_id = player.act_night(game_state)
        if target_id is not None:
            target_player = game_state.get_player(target_id)
            if target_player:
                # 狼人返回 Werewolf，其他返回 Good
                is_werewolf = target_player.role.faction == Faction.WEREWOLF
                return {"target": target_id, "is_werewolf": is_werewolf}
        return None


class Witch(Role):
    def __init__(self):
        super().__init__(RoleType.WITCH, Faction.GOD, "女巫", priority=30)
        self.has_antidote = True
        self.has_poison = True

    def perform_night_action(self, game_state, player):
        # 女巫夜晚的行动
        # action 格式可能为: {"save": True} 或 {"poison": target_id} 或 None
        action = player.act_night(game_state)
        if action:
            if action.get("save") and self.has_antidote:
                # 只有当晚有人被狼刀且有解药才能救，在 Game 中判断
                self.has_antidote = False
                return {"save": True}
            elif "poison" in action and self.has_poison:
                self.has_poison = False
                return {"poison": action["poison"]}
        return None


class Hunter(Role):
    def __init__(self):
        super().__init__(RoleType.HUNTER, Faction.GOD, "猎人", priority=0)

    def perform_night_action(self, game_state, player):
        # 猎人夜晚无主动技能（死亡开枪在 Game 结算白天/夜晚死亡时处理）
        return None


class Idiot(Role):
    def __init__(self):
        super().__init__(RoleType.IDIOT, Faction.GOD, "白痴", priority=0)

    def perform_night_action(self, game_state, player):
        # 白痴夜晚无主动技能
        return None
