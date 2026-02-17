
import random
from typing import List, Optional, Dict
from config import GAME_CONFIG, RoleType
from player import Player
from roles import *
from utils import logger

class WerewolfGame:
    def __init__(self):
        self.players: List[Player] = []
        self.day_count = 0
        self.winner: Optional[str] = None
        self.sheriff: Optional[Player] = None
        self._init_players()

    def _init_players(self):
        roles = []
        for role_type, count in GAME_CONFIG["role_counts"].items():
            for _ in range(count):
                if role_type == RoleType.WEREWOLF:
                    roles.append(Werewolf())
                elif role_type == RoleType.VILLAGER:
                    roles.append(Villager())
                elif role_type == RoleType.SEER:
                    roles.append(Seer())
                elif role_type == RoleType.WITCH:
                    roles.append(Witch())
                elif role_type == RoleType.HUNTER:
                    roles.append(Hunter())
                elif role_type == RoleType.IDIOT:
                    roles.append(Idiot())
        
        random.shuffle(roles)
        self.players = [Player(i+1, role) for i, role in enumerate(roles)]
        
        # Initialize Knowledge
        for p in self.players:
            p.initialize_knowledge(self.players, GAME_CONFIG)
        
        logger.info("Game Initialized with roles:")
        for p in self.players:
            logger.info(f"{p}")



    def get_alive_players(self) -> List[Player]:
        return [p for p in self.players if p.is_alive]

    def get_players_by_role(self, role_type: RoleType) -> List[Player]:
        return [p for p in self.players if p.role.role_type == role_type]

    def check_win_condition(self) -> bool:
        alive = self.get_alive_players()
        wolves = [p for p in alive if p.role.role_type == RoleType.WEREWOLF]
        villagers = [p for p in alive if p.role.role_type == RoleType.VILLAGER]
        gods = [p for p in alive if p.role.role_type not in (RoleType.WEREWOLF, RoleType.VILLAGER)]
        
        if not wolves:
            self.winner = "Good"
            logger.info("Game Over! Winner: Good (All Wolves Dead)")
            return True
            
        if not villagers:
            self.winner = "Werewolves"
            logger.info("Game Over! Winner: Werewolves (All Villagers Dead - Slaughter)")
            return True
            
        if not gods:
            self.winner = "Werewolves"
            logger.info("Game Over! Winner: Werewolves (All Gods Dead - Slaughter)")
            return True
            
        return False


    def run_night(self) -> Dict[Player, str]:
        self.day_count += 1
        logger.info(f"\n--- Night {self.day_count} ---")
        
        # Dictionary to track night deaths {Player: Reason}
        deaths = {} 
        
        # 1. Werewolves Action
        wolves = self.get_players_by_role(RoleType.WEREWOLF)
        alive_wolves = [p for p in wolves if p.is_alive]
        
        if alive_wolves:
            votes = {}
            alive_players = self.get_alive_players()
            
            for wolf in alive_wolves:
                # Delegate to Role
                target = wolf.role.choose_kill_target(alive_players, wolf.knowledge_prob)
                if target:
                    votes[target] = votes.get(target, 0) + 1
                    logger.debug(f"Wolf {wolf.id} votes for {target}")

            if votes:
                max_votes = max(votes.values())
                top_targets = [t for t, count in votes.items() if count == max_votes]
                wolf_kill = random.choice(top_targets)
                logger.info(f"Wolves decided to kill {wolf_kill} (Votes: {max_votes}/{len(alive_wolves)})")
                deaths[wolf_kill] = "Wolf"

        # 2. Seer Action
        seer_list = self.get_players_by_role(RoleType.SEER)
        seer = seer_list[0] if seer_list else None
        if seer and seer.is_alive and isinstance(seer.role, Seer):
            check_target = seer.role.choose_check_target(self.get_alive_players(), seer.knowledge_prob)
            if check_target:
                seer.role.checked_players.append(check_target.id)
                is_wolf = check_target.role.role_type == RoleType.WEREWOLF
                logger.info(f"Seer {seer.id} checked {check_target.id} ({check_target.role.name}). Valid: {is_wolf}")
                
                # Update info
                fate = RoleType.WEREWOLF if is_wolf else RoleType.VILLAGER
                seer.mark_role_certain(check_target.id, fate)

        # 3. Witch Action
        witch_list = self.get_players_by_role(RoleType.WITCH)
        witch = witch_list[0] if witch_list else None
        
        if witch and witch.is_alive and isinstance(witch.role, Witch):
            used_drug = False
            # Save Logic
            if wolf_kill and wolf_kill in deaths:
                if witch.role.choose_save_decision(wolf_kill, witch.knowledge_prob):
                    logger.info(f"Witch used antidote on {wolf_kill.id}")
                    witch.role.use_antidote()
                    del deaths[wolf_kill]
                    wolf_kill.saved = True
                    used_drug = True
            
            # Poison Logic
            # Only allow poison if no drug used yet (Antidote and Poison cannot be used same night)
            if not used_drug:
                poison_target = witch.role.choose_poison_target(self, [p for p in self.get_alive_players() if p != witch], witch.knowledge_prob)
                if poison_target:
                    logger.info(f"Witch uses poison on Player {poison_target.id}")
                    witch.role.use_poison()
                    deaths[poison_target] = "Witch"
                    poison_target.poisoned = True


        return deaths


    def run_day(self, night_deaths: Dict[Player, str]):
        # Day count matches the preceding night count
        logger.info(f"\n--- Day {self.day_count} ---")
        
        # 1. Sheriff Election (Day 1 only if enabled)
        if self.day_count == 1 and GAME_CONFIG.get("sheriff_enabled", False):
            self.run_sheriff_election()

        # 2. Announce Deaths
        current_deaths = []
        if not night_deaths:
            logger.info("平安夜 (No one died last night).")
        else:
            for p in night_deaths:
                logger.info(f"Player {p.id} died last night.")
                p.die()
                current_deaths.append(p)
            
            # Transfer Sheriff if needed
            for p in current_deaths:
                self.handle_sheriff_death(p)
                # Handle Role Death Actions (e.g. Hunter)
                p.role.on_death(self, p)

        if self.check_win_condition(): return

        # 3. Discussion (Simplified)
        # Verify Seer info sharing
        self.share_information()

        # 4. Voting
        self.run_voting_phase()
        
        self.check_win_condition()

    def run_sheriff_election(self):
        logger.info("Running Sheriff Election...")
        alive_players = self.get_alive_players()
        
        # 1. Identify Candidates
        candidates = []
        for p in alive_players:
            if p.role.sheriff_candidacy_prob > 0.5:
                candidates.append(p)
                logger.info(f"Player {p.id} ({p.role.name}) runs for Sheriff.")
        
        if not candidates:
            logger.info("No candidates for Sheriff.")
            return

        # 2. Candidates Share Information
        logger.info("Candidates share information:")
        for c in candidates:
            c.role.share_information(c, self.players)
            
        # 3. Vote / Elect
        # Prompt: "最后预言家当选警长" (Seer wins)
        # We look for Seers among candidates (random among seers if multiple)
        seers = [p for p in candidates if p.role.role_type == RoleType.SEER]
        
        if seers:
            self.sheriff = random.choice(seers)
        else:
            # If Seer is not running (dead?), pick random candidate or Witch?
            # Default to random candidate if Seer dead
            self.sheriff = random.choice(candidates)
            
        self.sheriff.sheriff = True
        logger.info(f"Sheriff is Player {self.sheriff.id} ({self.sheriff.role.name})")

    def share_information(self):
        # Delegate to roles
        for p in self.get_alive_players():
            p.role.share_information(p, self.players)

    
    def run_voting_phase(self):
        candidates = self.get_alive_players()
        if not candidates: return

        votes = {}
        # Logic: 
        # Wolves vote together for a good guy (usually one with 'strongest' info or random)
        # Good guys vote for confirmed wolves or random suspects
        
        wolves = [p for p in candidates if p.role.role_type == RoleType.WEREWOLF]
        good = [p for p in candidates if p.role.role_type != RoleType.WEREWOLF]
        
        # Decide Targets
        wolf_target = None
        if good:
            wolf_target = random.choice(good)
            
        confirmed_wolves = []
        seers = self.get_players_by_role(RoleType.SEER)
        if seers and seers[0].is_alive:
            for pid, probs in seers[0].knowledge_prob.items():
                 # Check for Wolf certainty
                 if probs.get(RoleType.WEREWOLF, 0) >= 0.99:
                    # Find alive player
                     for p in candidates:
                         if p.id == pid:
                             confirmed_wolves.append(p)

        # Cast Votes
        for voter in candidates:
            # Candidates to vote FOR (usually anyone alive)
            # Self-voting allowed? usually yes.
            valid_targets = [p for p in candidates] # Everyone is a valid target
            
            # Delegate to Role
            vote_target = voter.role.vote(self, valid_targets, voter.knowledge_prob)
            
            # Fallback if None (e.g. no info)? Random other
            if not vote_target:
                 others = [p for p in candidates if p != voter]
                 if others:
                     vote_target = random.choice(others)

            
            if vote_target:
                # Sheriff vote counts as 1.5 or 2? Standard is 1.5, allow config or assume 1.5
                weight = 1.5 if voter.sheriff else 1.0
                votes[vote_target] = votes.get(vote_target, 0) + weight
                logger.info(f"Player {voter.id} votes -> {vote_target.id}")

        # Tally
        if votes:
            # Log vote counts
            vote_details = ", ".join([f"Player {p.id}: {c}" for p, c in votes.items()])
            logger.info(f"Vote Counts: {vote_details}")
            
            max_votes = max(votes.values())
            executed_candidates = [p for p, c in votes.items() if c == max_votes]
            executed = random.choice(executed_candidates)
            
            logger.info(f"Voting Result: Player {executed.id} is executed!")
            
            # Delegate execution handling to Role (e.g. Idiot check)
            executed.role.handle_vote_execution(self, executed)

    def handle_sheriff_death(self, dead_player: Player):
        if self.sheriff != dead_player:
            return
            
        logger.info(f"Sheriff {dead_player.id} died. Transferring badge...")
        self.sheriff.sheriff = False
        
        candidates = self.get_alive_players()
        if not candidates:
            self.sheriff = None
            return

        next_sheriff = dead_player.role.choose_successor(self, candidates, dead_player.knowledge_prob)
        
        if next_sheriff:
            self.sheriff = next_sheriff
            self.sheriff.sheriff = True
            logger.info(f"New Sheriff is Player {self.sheriff.id}")
        else:
             self.sheriff = None

    def get_badge_flow_target(self) -> Optional[int]:
        """
        Find the current Seer and return their badge flow target.
        Only valid if the Seer is alive and is the Sheriff.
        """
        for p in self.players:
            if p.role.role_type == RoleType.SEER and p.is_alive and p.sheriff:
                return getattr(p.role, 'badge_flow_target', None)
        return None


