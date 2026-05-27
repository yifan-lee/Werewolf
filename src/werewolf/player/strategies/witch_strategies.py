import random
from typing import Any
from .base_strategies import BaseRandomStrategy

class WitchRandomStrategy(BaseRandomStrategy):
    def act_night(self, player: 'Player', game_state: 'Game') -> Any:
        alive_others = [p.player_id for p in game_state.get_alive_players() if p.player_id != player.player_id]
        action = {}
        if player.role.has_antidote and game_state.current_wolf_kill:
            if random.random() < 0.5:
                action["save"] = True
                return action
        if player.role.has_poison and alive_others:
            if random.random() < 0.3:
                action["poison"] = random.choice(alive_others)
                return action
        return None
