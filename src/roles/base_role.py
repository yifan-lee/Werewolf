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

class VillagerRole(BaseRole):
    def __init__(self):
        super().__init__("Villager")

    def handle_night_action(self, player_obj, context):
        pass

    def handle_day_action(self, player_obj, context):
        pass