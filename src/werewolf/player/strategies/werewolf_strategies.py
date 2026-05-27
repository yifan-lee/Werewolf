import random
from typing import Any
from .base_strategies import BaseRandomStrategy
from ...constants import Faction

class WerewolfRandomStrategy(BaseRandomStrategy):
    def act_night(self, player: 'Player', game_state: 'Game') -> Any:
        alive_non_wolves = [
            p.player_id for p in game_state.get_alive_players() 
            if p.role.faction != Faction.WEREWOLF
        ]
        return random.choice(alive_non_wolves) if alive_non_wolves else None
        
    def update_belief_after_speech(self, player: 'Player', speaker_id: int, speech: str, game_state: 'Game'):
        pass

# 以后这里可以加入:
# class WerewolfLLMStrategy(BaseLLMStrategy): ...
