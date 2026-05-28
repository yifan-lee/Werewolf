from roles.role import Role
from config import RoleType
from typing import TYPE_CHECKING
from utils import logger

if TYPE_CHECKING:
    from game import WerewolfGame
    from player import Player

class Idiot(Role):
    def __init__(self):
        super().__init__(RoleType.IDIOT)
        self.revealed = False
        
    def reveal(self):
        self.revealed = True

    def handle_vote_execution(self, game: 'WerewolfGame', my_player: 'Player') -> bool:
        if not self.revealed:
            # First time voted out: Reveal and survive
            self.revealed = True
            
            logger.info(f"Player {my_player.id} flips card: I am an IDIOT!")
            
            # Update all players' knowledge
            
            for p in game.players:
                p.mark_role_certain(my_player.id, RoleType.IDIOT)
                
            logger.info("Idiot survives execution.")
            return False
        else:
            # Already revealed: Die
            return super().handle_vote_execution(game, my_player)
