import random
from typing import Any
from .base_strategies import BaseRandomStrategy

class HunterRandomStrategy(BaseRandomStrategy):
    def act_night(self, player: 'Player', game_state: 'Game') -> Any:
        alive_others = [p.player_id for p in game_state.get_alive_players() if p.player_id != player.player_id]
        return random.choice(alive_others) if alive_others else None
