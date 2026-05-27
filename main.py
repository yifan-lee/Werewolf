from werewolf.constants import WinCondition, RoleType
from werewolf.roles import Werewolf, Villager, Seer, Witch, Hunter, Idiot
from werewolf.player.strategies import (
    WerewolfHeuristicStrategy, VillagerRandomStrategy, SeerRandomStrategy, 
    WitchRandomStrategy, HunterRandomStrategy, IdiotRandomStrategy
)
from werewolf.simulator import GameConfig, Simulator

def main():
    # 默认 12 人局板子：4狼 4民 4神 (预女猎白)
    roles_setup = [
        Werewolf(), Werewolf(), Werewolf(), Werewolf(),
        Villager(), Villager(), Villager(), Villager(),
        Seer(), Witch(), Hunter(), Idiot()
    ]
    
    strategy_mapping = {
        RoleType.WEREWOLF: WerewolfHeuristicStrategy,
        RoleType.VILLAGER: VillagerRandomStrategy,
        RoleType.SEER: SeerRandomStrategy,
        RoleType.WITCH: WitchRandomStrategy,
        RoleType.HUNTER: HunterRandomStrategy,
        RoleType.IDIOT: IdiotRandomStrategy
    }
    
    # 初始化 GameConfig，传入板子配置和策略映射
    config = GameConfig(
        roles_setup=roles_setup,
        strategy_mapping=strategy_mapping,
        win_condition=WinCondition.KILL_SIDE  # 屠边局
    )
    
    # 初始化模拟器，模拟跑 100 局，串行执行方便看日志或者排查bug，可以设为 parallel=True 提速
    simulator = Simulator(config, num_games=1000)
    
    # 开始运行 MCMC (Monte Carlo) 模拟
    simulator.run(parallel=True)

if __name__ == "__main__":
    main()
