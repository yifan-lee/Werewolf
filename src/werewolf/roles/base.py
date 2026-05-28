from ..constants import Faction, RoleType
from typing import Any

class Role:
    def __init__(self, role_type: RoleType, faction: Faction, name: str, priority: int = 0):
        self.role_type = role_type
        self.faction = faction
        self.name = name
        self.priority = priority  # 夜晚行动优先级，数字越大/越小可自定义（这里不强制依赖）

    def perform_night_action(self, game_state: Any, player: Any) -> Any:
        """执行该角色的夜间技能（若有）。"""
        pass

    def __repr__(self):
        return self.name
