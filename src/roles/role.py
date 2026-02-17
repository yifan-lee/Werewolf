

from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING, Dict, Optional
from config import RoleType

if TYPE_CHECKING:
    from player import Player
    from game import WerewolfGame

class Role(ABC):
    def __init__(self, role_type: RoleType):
        self.role_type = role_type
        self.sheriff_candidacy_prob = 0.0 # Probability to run for Sheriff

    @property
    def name(self):
        return self.role_type.value

    def __str__(self):
        return self.name

    def share_information(self, my_player: 'Player', all_players: List['Player']):
        """
        Share information during day phase.
        Default implementation does nothing.
        """
        pass

    def choose_successor(self, game: 'WerewolfGame', alive_players: List['Player'], knowledge_prob: Dict[str, any]) -> 'Player':
        """
        Choose a successor for Sheriff if this player dies as Sheriff.
        Default: Random alive player.
        """
        import random
        if not alive_players:
            return None
        return random.choice(alive_players)

    def on_death(self, game: 'WerewolfGame', my_player: 'Player'):
        """
        Handle death of the player (e.g. Hunter shoots).
        Default: Do nothing.
        """
        pass

    def vote(self, game: 'WerewolfGame', alive_players: List['Player'], knowledge_prob: Dict[int, Dict[RoleType, float]]) -> Optional['Player']:
        """
        Vote for a player during the day.
        Default (Good): Vote for the player with highest Werewolf probability.
        """
        best_target = None
        max_wolf_prob = -1.0
        
        badge_flow_target_id = game.get_badge_flow_target()
        
        for p in alive_players:
             # Skip badge flow target if I am Good
             if self.role_type != RoleType.WEREWOLF and badge_flow_target_id is not None and p.id == badge_flow_target_id:
                 continue

             probs = knowledge_prob.get(p.id, {})
             wolf_prob = probs.get(RoleType.WEREWOLF, 0.0)
             
             if wolf_prob > max_wolf_prob:
                 max_wolf_prob = wolf_prob
                 best_target = p
                  
        return best_target

    def handle_vote_execution(self, game: 'WerewolfGame', my_player: 'Player') -> bool:
        """
        Handle the event when the player is voted out during the day.
        Returns: True if the player died, False if they survived (e.g. Idiot).
        Default: Player dies.
        """
        my_player.die()
        game.handle_sheriff_death(my_player)
        self.on_death(game, my_player)
        return True


