import argparse
import logging
from game import WerewolfGame
from utils import logger

def run_simulation():
    game = WerewolfGame()
    while not game.winner:
        night_deaths = game.run_night()
        game.run_day(night_deaths)
        if game.winner:
            return game.winner
    return game.winner

def main():
    parser = argparse.ArgumentParser(description="Werewolf Simulator benchmark tool")
    parser.add_argument("-n", "--num_games", type=int, default=1, help="Number of games to simulate")
    args = parser.parse_args()

    if args.num_games > 1:
        # Suppress logs for benchmarking
        logger.setLevel(logging.WARNING)
        print(f"Running {args.num_games} games...")
        
        results = {}
        for i in range(args.num_games):
            if i % 10 == 0:
                print(f"\rProgress: {i}/{args.num_games}", end="", flush=True)
            winner = run_simulation()
            results[winner] = results.get(winner, 0) + 1
        
        print(f"\rProgress: {args.num_games}/{args.num_games}")
        print("\n--- Benchmark Results ---")
        for faction, wins in results.items():
            percentage = (wins / args.num_games) * 100
            print(f"{faction}: {wins} wins ({percentage:.2f}%)")
    else:
        logger.info("Starting Werewolf Game Simulation...")
        winner = run_simulation()
        logger.info(f"\nGame Over! Winner: {winner}")

if __name__ == "__main__":
    main()
