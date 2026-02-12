from .base_role import BaseRole


class IdiotRole(BaseRole):
    def __init__(self):
        super().__init__("Idiot")

    def handle_night_action(self, player_obj, context):
        # 逻辑：查看 context 中的 alive_players
        # 结合 player_obj.beliefs 找到最像预言家或女巫的人
        pass

    def handle_day_action(self, player_obj, context):
        pass