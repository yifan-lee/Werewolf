from werewolf.constants import WinCondition, RoleType
from werewolf.roles import Werewolf, Villager, Seer, Witch, Hunter, Idiot
from werewolf.player.strategies import (
    WerewolfBasicStrategy, VillagerBasicStrategy, SeerBasicStrategy, 
    WitchBasicStrategy, HunterBasicStrategy, IdiotBasicStrategy
)
from werewolf.simulator import GameConfig
from werewolf.game.game import Game
import random

def main():
    roles_setup = [
        Werewolf(), Werewolf(), Werewolf(), Werewolf(),
        Villager(), Villager(), Villager(), Villager(),
        Seer(), Witch(), Hunter(), Idiot()
    ]
    
    strategy_mapping = {
        RoleType.WEREWOLF: WerewolfBasicStrategy,
        RoleType.VILLAGER: VillagerBasicStrategy,
        RoleType.SEER: SeerBasicStrategy,
        RoleType.WITCH: WitchBasicStrategy,
        RoleType.HUNTER: HunterBasicStrategy,
        RoleType.IDIOT: IdiotBasicStrategy
    }
    
    config = GameConfig(
        roles_setup=roles_setup,
        strategy_mapping=strategy_mapping,
        win_condition=WinCondition.KILL_SIDE
    )
    
    random.seed(42)
    players = config.create_players()
    game = Game(players, config.win_condition)
    res = game.run()
    
    for log in game.logs:
        print(log)
    print("WINNER:", res)

if __name__ == "__main__":
    main()
