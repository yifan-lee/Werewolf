import random
from typing import Any, Dict
from ..strategy import Strategy

class BaseRandomStrategy(Strategy):
    """
    提供随机策略的基础实现，处理所有白天共用的投票、发言逻辑。
    夜晚逻辑 act_night 和复杂的 update_belief 由具体子类重写。
    """
    
    def act_night(self, player: 'Player', game_state: 'Game') -> Any:
        return None

    def elect_sheriff_strategy(self, player: 'Player', game_state: 'Game') -> Dict[str, Any]:
        res = {"run_for_sheriff": False, "vote_for": None}
        if random.random() < 0.5:
            res["run_for_sheriff"] = True
        return res

    def speech_day_strategy(self, player: 'Player', game_state: 'Game') -> str:
        return f"我是好人，过。(来自 {player.role.name} 的随机发言)"

    def last_words_strategy(self, player: 'Player', game_state: 'Game') -> str:
        return "我是好人，我死得很冤。"

    def update_belief_after_speech(self, player: 'Player', speaker_id: int, speech: str, game_state: 'Game'):
        pass

    def update_belief_after_last_words(self, player: 'Player', speaker_id: int, last_words: str, game_state: 'Game'):
        pass

    def vote_day_strategy(self, player: 'Player', game_state: 'Game') -> int:
        alive_others = [p.player_id for p in game_state.get_alive_players() if p.player_id != player.player_id]
        if alive_others:
            return random.choice(alive_others)
        return None

    def transfer_sheriff_strategy(self, player: 'Player', game_state: 'Game') -> int:
        alive_others = [p.player_id for p in game_state.get_alive_players() if p.player_id != player.player_id]
        if alive_others:
            return random.choice(alive_others)
        return None
