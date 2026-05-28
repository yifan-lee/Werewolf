from werewolf.game.game import Game
from werewolf.player.player import Player
import random
from typing import Any
from .base_strategies import BasicStrategy

class HunterBasicStrategy(BasicStrategy):
    def execute_death_effect(self, player: 'Player', game_state: 'Game') -> Any:
        
