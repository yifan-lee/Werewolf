

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
            badge_flow_target_id = game.get_badge_flow_target()
            
            targets = [p for p in game.get_alive_players() if p.id != badge_flow_target_id and p.id != my_player.id]
            if targets:
                # Select target with highest Wolf probability
                shot = None
                max_wolf_prob = -1.0
                
                for p in targets:
                    probs = my_player.knowledge_prob.get(p.id, {})
                    wolf_prob = probs.get(RoleType.WEREWOLF, 0.0)
                    if wolf_prob > max_wolf_prob:
                        max_wolf_prob = wolf_prob
                        shot = p
                
                if shot:
                    logger.info(f"Hunter shoots Player {shot.id} (Wolf Prob: {max_wolf_prob:.2f})")
                    shot.die()
                    
                    # Handle consequences of shot player dying
                    game.handle_sheriff_death(shot)
                    # Recursive death handling
                    shot.role.on_death(game, shot)

