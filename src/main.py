
from game import WerewolfGame
from utils import logger

def main():
    logger.info("Starting Werewolf Game Simulation...")
    game = WerewolfGame()
    
    while not game.winner:
        # Night Phase
        night_deaths = game.run_night()
        
        # Day Phase
        game.run_day(night_deaths)
        
        if game.winner:
            break
            
    logger.info(f"\nGame Over! Winner: {game.winner}")

if __name__ == "__main__":
    main()
