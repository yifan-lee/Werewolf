from werewolf.constants import WinCondition
from werewolf.roles.concrete import Werewolf, Villager, Seer, Witch, Hunter, Idiot
from werewolf.player.random_strategy import RandomStrategy
from werewolf.simulator import GameConfig, Simulator

def main():
    # 默认 12 人局板子：4狼 4民 4神 (预女猎白)
    roles_setup = [
        Werewolf(), Werewolf(), Werewolf(), Werewolf(),
        Villager(), Villager(), Villager(), Villager(),
        Seer(), Witch(), Hunter(), Idiot()
    ]
    
    # 初始化 GameConfig，传入板子配置和采用的策略类
    config = GameConfig(
        roles_setup=roles_setup,
        strategy_class=RandomStrategy,
        win_condition=WinCondition.KILL_SIDE  # 屠边局
    )
    
    # 初始化模拟器，模拟跑 100 局，串行执行方便看日志或者排查bug，可以设为 parallel=True 提速
    simulator = Simulator(config, num_games=100)
    
    # 开始运行 MCMC (Monte Carlo) 模拟
    simulator.run(parallel=True)

if __name__ == "__main__":
    main()
