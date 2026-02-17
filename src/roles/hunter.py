

from roles.role import Role
from config import RoleType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game import WerewolfGame
    from player import Player


class Hunter(Role):
    def __init__(self):
        super().__init__(RoleType.HUNTER)

    def on_death(self, game: 'WerewolfGame', my_player: 'Player'):
        from utils import logger
        import random
        
        # Check if poisoned (Witch logic interaction needed, but for now allow shoot)
        if not my_player.poisoned:
            logger.info(f"Hunter {my_player.id} triggers skill!")
            targets = game.get_alive_players()
            if targets:
                shot = random.choice(targets)
                logger.info(f"Hunter shoots Player {shot.id}")
                shot.die()
                
                # Handle consequences of shot player dying
                game.handle_sheriff_death(shot)
                # Recursive death handling
                shot.role.on_death(game, shot)

