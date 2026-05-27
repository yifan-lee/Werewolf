from enum import Enum, auto

class Faction(Enum):
    VILLAGER = "Villager"      # 平民
    GOD = "God"                # 神职
    WEREWOLF = "Werewolf"      # 狼人

class RoleType(Enum):
    VILLAGER = "Villager"
    WEREWOLF = "Werewolf"
    SEER = "Seer"
    WITCH = "Witch"
    HUNTER = "Hunter"
    IDIOT = "Idiot"

class GamePhase(Enum):
    NIGHT = "Night"
    DAY_ELECTION = "Day_Election"   # 竞选警长阶段
    DAY_SPEECH = "Day_Speech"       # 发言阶段
    DAY_VOTE = "Day_Vote"           # 投票放逐阶段
    GAME_OVER = "Game_Over"

class GameResult(Enum):
    WEREWOLF_WIN = "Werewolf_Win"
    GOOD_WIN = "Good_Win"
    DRAW = "Draw"

class WinCondition(Enum):
    KILL_ALL = "Kill_All"             # 屠城
    KILL_SIDE = "Kill_Side"           # 屠边

