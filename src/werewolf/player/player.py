from typing import Any, Dict
from .strategy import Strategy

class Player:
    def __init__(self, player_id: int, role: Any, strategy: Strategy):
        self.player_id = player_id
        self.role = role
        self.strategy = strategy
        self.is_alive = True
        
        # 白痴的被动状态
        self.is_idiot_revealed = False  # 如果是白痴且被放逐翻牌，则为 True，失去投票权和被选举权
        
        # 认知状态 (belief state)，初始可以是一个空的字典，或者在游戏开始时由策略初始化
        self.belief_state: Dict[str, Any] = {}

    def act_night(self, game_state: Any) -> Any:
        return self.strategy.act_night(self, game_state)

    def elect_sheriff_strategy(self, game_state: Any) -> Dict[str, Any]:
        return self.strategy.elect_sheriff_strategy(self, game_state)

    def speech_day_strategy(self, game_state: Any) -> str:
        return self.strategy.speech_day_strategy(self, game_state)

    def last_words_strategy(self, game_state: Any) -> str:
        return self.strategy.last_words_strategy(self, game_state)

    def update_belief_after_speech(self, speaker_id: int, speech: str, game_state: Any):
        self.strategy.update_belief_after_speech(self, speaker_id, speech, game_state)

    def update_belief_after_last_words(self, speaker_id: int, last_words: str, game_state: Any):
        self.strategy.update_belief_after_last_words(self, speaker_id, last_words, game_state)

    def vote_day_strategy(self, game_state: Any) -> int:
        if self.is_idiot_revealed:
            return None  # 翻牌白痴没有投票权
        return self.strategy.vote_day_strategy(self, game_state)

    def transfer_sheriff_strategy(self, game_state: Any) -> int:
        return self.strategy.transfer_sheriff_strategy(self, game_state)

    def __repr__(self):
        status = "Alive" if self.is_alive else "Dead"
        return f"<Player {self.player_id}: {self.role.name} ({status})>"
