

from roles.role import Role
from config import RoleType
from typing import TYPE_CHECKING, List, Dict
import random
from utils import logger

if TYPE_CHECKING:
    from game import WerewolfGame
    from player import Player


class Hunter(Role):
    def __init__(self):
        super().__init__(RoleType.HUNTER)
        self.revealed = False

    def share_information(self, my_player: 'Player', all_players: List['Player']):
        # Hunter reveals if they think the Seer is dead
        if self.revealed:
            return

        seer_dead = False
        for pid, probs in my_player.knowledge_prob.items():
            if probs.get(RoleType.SEER, 0.0) > 0.99:
                # Found someone I believe is the Seer
                target_p = next((p for p in all_players if p.id == pid), None)
                if target_p and not target_p.is_alive:
                    seer_dead = True
                    break
        
        if seer_dead:
            self.revealed = True
            logger.info(f"[Discussion] Hunter {my_player.id} says: Identifying myself as the Hunter because the Seer is dead!")
            # Everyone marks me as Certain Hunter
            for p in all_players:
                p.mark_role_certain(my_player.id, RoleType.HUNTER)

    def on_death(self, game: 'WerewolfGame', my_player: 'Player'):
        
        
        # Check if poisoned (Witch logic interaction needed, but for now allow shoot)
        if not my_player.poisoned:
            logger.info(f"Hunter {my_player.id} triggers skill!")
            badge_flow_target_id = game.get_badge_flow_target()
            
            targets = [p for p in game.get_alive_players() if p.id != badge_flow_target_id and p.id != my_player.id]
            if targets:
                # Select targets with highest Wolf probability (random among ties)
                best_targets = []
                max_wolf_prob = -1.0
                
                for p in targets:
                    probs = my_player.knowledge_prob.get(p.id, {})
                    wolf_prob = probs.get(RoleType.WEREWOLF, 0.0)
                    if wolf_prob > max_wolf_prob:
                        max_wolf_prob = wolf_prob
                        best_targets = [p]
                    elif wolf_prob == max_wolf_prob and max_wolf_prob >= 0:
                        best_targets.append(p)
                
                if best_targets:
                    shot = random.choice(best_targets)
                    logger.info(f"Hunter shoots Player {shot.id} (Wolf Prob: {max_wolf_prob:.2f})")
                    shot.die()
                    
                    # Handle consequences of shot player dying
                    game.handle_sheriff_death(shot)
                    # Recursive death handling
                    shot.role.on_death(game, shot)

