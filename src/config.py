
from enum import Enum

class RoleType(Enum):
    WEREWOLF = "狼人"
    VILLAGER = "平民"
    SEER = "预言家"
    WITCH = "女巫"
    HUNTER = "猎人"
    IDIOT = "白痴"

GAME_CONFIG = {
    "role_counts": {
        RoleType.WEREWOLF: 4,
        RoleType.VILLAGER: 4,
        RoleType.SEER: 1,
        RoleType.WITCH: 1,
        RoleType.HUNTER: 1,
        RoleType.IDIOT: 1,
    },
    "sheriff_enabled": True, # Can be toggled
}
