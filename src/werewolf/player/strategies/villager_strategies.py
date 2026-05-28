from werewolf.game.game import Game
from werewolf.player.player import Player
import random
from typing import Any, Dict, Tuple
from .base_strategies import BasicStrategy

class VillagerBasicStrategy(BasicStrategy):
    def last_words_strategy(self, player: 'Player', game_state: 'Game') -> Tuple[str, Dict[str, Any]]:
        return "我是好人，我死得很冤。", {}
