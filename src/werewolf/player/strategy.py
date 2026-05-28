from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple

class Strategy(ABC):
    """
    策略基类。定义了玩家在各个阶段所能做出的决策接口。
    具体的AI或者随机策略都需要继承该类。
    """
    
    def __init__(self):
        self.memory: Dict[str, Any] = {}

    @abstractmethod
    def act_night(self, player: 'Player', game_state: 'Game') -> Any:
        """夜晚行动策略。例如狼人选择刀谁，女巫选择救谁或毒谁。"""
        pass

    @abstractmethod
    def receive_night_feedback(self, player: 'Player', result: Any):
        """接收夜晚行动的客观结算结果（例如验人结果）"""
        pass

    @abstractmethod
    def elect_sheriff_strategy(self, player: 'Player', game_state: 'Game') -> Dict[str, Any]:
        """
        竞选警长策略。
        应该返回一个字典，例如：
        {"run_for_sheriff": True, "vote_for": 3}
        如果是警上玩家，决定是否退水；如果是警下玩家，决定投票给哪位竞选者。
        """
        pass
    
    @abstractmethod
    def speech_day_strategy(self, player: 'Player', game_state: 'Game') -> Tuple[str, Dict[str, Any]]:
        """白天常规发言策略。返回 (发言文字内容, 结构化语义标签)"""
        pass

    @abstractmethod
    def last_words_strategy(self, player: 'Player', game_state: 'Game') -> Tuple[str, Dict[str, Any]]:
        """发表遗言策略。返回 (遗言文字内容, 结构化语义标签)"""
        pass

    @abstractmethod
    def update_belief_after_speech(self, player: 'Player', speaker_id: int, speech: str, claims: Dict[str, Any], game_state: 'Game'):
        """在白天某人发完言后，更新自己的信念/知识库。"""
        pass

    @abstractmethod
    def update_belief_after_badge_transfer(self, player: 'Player', dead_sheriff_id: int, new_sheriff_id: int, game_state: 'Game'):
        """在警徽移交或撕毁后，更新自己的信念/知识库。"""
        pass

    @abstractmethod
    def update_belief_after_last_words(self, player: 'Player', speaker_id: int, last_words: str, claims: Dict[str, Any], game_state: 'Game'):
        """听到遗言后，更新自身的 belief_state"""
        pass

    @abstractmethod
    def vote_day_strategy(self, player: 'Player', game_state: 'Game') -> Tuple[int, str]:
        """白天放逐投票策略。返回 (投票的玩家ID, 投票理由)。如果弃票返回 (None, 理由)。"""
        pass

    @abstractmethod
    def transfer_sheriff_strategy(self, player: 'Player', game_state: 'Game') -> int:
        """死亡时移交警长策略。返回要移交的玩家 ID，或者 None 表示撕毁警徽。"""
        pass
