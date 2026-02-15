class Player:
    def __init__(self, player_id):
        self.player_id = player_id
        self.is_alive = True

        # 对其他玩家身份的认知
        # 结构：{ player_id: { "Wolf": 0.2, "Villager": 0.4, "Seer": 0.1, ... } }
        self.beliefs = {}

        # 金水和银水的来源（记录谁宣称过这个信息）
        # 结构：{ player_id_of_claimer: "Good" }
        self.gold_water_claims = {}  # 预言家发出的金水
        self.silver_water_claims = {} # 女巫发出的银水

        # 公开宣称的身份
        self.public_role_claim = None

    def update_belief(self, target_id, role_probs):
        """
        用于后续更新认知，role_probs 是一个字典，如 {"Wolf": 0.8, "Villager": 0.2}
        """
        self.beliefs[target_id] = role_probs