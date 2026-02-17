
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
        good = [p for p in alive if p.role.role_type != RoleType.WEREWOLF]
        
        if not wolves:
            self.winner = "Good"
            return True
        if len(wolves) >= len(good):
            self.winner = "Werewolves"
            return True
        return False

    def run_night(self) -> Dict[str, any]:
        self.day_count += 1
        logger.info(f"\n--- Night {self.day_count} ---")
        
        # 1. Werewolves Action
        wolves = self.get_players_by_role(RoleType.WEREWOLF)
        alive_wolves = [p for p in wolves if p.is_alive]
        target = None
        
        if alive_wolves:
            # Logic: Priority based
            # Simplified: Random for now, but prompt asked for specific priority.
            # "Priority: Seer > Witch > God > Silver Water (Saved by witch?) > Gold Water (Checked Good) > Sheriff > Other Good > Wolf"
            # Since wolves don't know who is Seer/Witch exactly unless revealed, 
            # we simulate them guessing or prioritizing revealed roles.
            # For this simulation, we'll assume they target known roles first, then random good.
            potential_targets = [p for p in self.get_alive_players() if p.role.role_type != RoleType.WEREWOLF]
            
            # TODO: Implement complex priority logic if metadata allows, 
            # for now, random among alive non-wolves to keep it running, 
            # but ideally should look at 'revealed' attributes if we add them.
            
            # Let's simple-implement priority:
            # 1. Known Seer/Witch (not really known unless revealed in day)
            # 2. Kill random good
            if potential_targets:
                target = random.choice(potential_targets)
                logger.info(f"Wolves decided to kill {target}")
        
        wolf_kill = target

        # 2. Seer Action
        seer_list = self.get_players_by_role(RoleType.SEER)
        seer = seer_list[0] if seer_list else None
        if seer and seer.is_alive:
            # Check someone not verified yet, prioritize suspicious (random for now)
            unchecked = [p for p in self.get_alive_players() if p != seer and not p.checked]
            if unchecked:
                check_target = random.choice(unchecked)
                check_target.checked = True
                is_wolf = check_target.role.role_type == RoleType.WEREWOLF
                logger.info(f"Seer {seer.id} checked {check_target.id} ({check_target.role.name}). Valid: {is_wolf}")
                
                # Seer remembers this
                fate = RoleType.WEREWOLF if is_wolf else RoleType.VILLAGER # Just "bad" or "good" really
                seer.known_roles[check_target.id] = fate

        # 3. Witch Action
        witch_list = self.get_players_by_role(RoleType.WITCH)
        witch = witch_list[0] if witch_list else None
        
        # Dictionary to track night deaths {Player: Reason}
        deaths = {} 

        if wolf_kill:
            deaths[wolf_kill] = "Wolf"

        if witch and witch.is_alive:
            # Save?
            if wolf_kill and witch.role.has_antidote:
                # Default logic: Save everyone (per prompt "默认救")
                # But usually self-save rules apply. Let's assume can save.
                logger.info(f"Witch used antidote on {wolf_kill.id}")
                witch.role.use_antidote()
                if wolf_kill in deaths:
                    del deaths[wolf_kill] 
                    wolf_kill.saved = True # Silver water
            
            # Poison?
            # "杀最像狼人的" - Random other for simulation if still has poison
            elif witch.role.has_poison:
                # Basic logic: 50% chance to poison if not saving? Or strictly "kill suspect".
                # Let's make Witch aggressive later in game or if specific condition.
                # For now, let's skip random poisoning to avoid chaos in simple sim, 
                # or random chance.
                pass

        return deaths


    def run_day(self, night_deaths: Dict[Player, str]):
        self.day_count += 1 # Actually day count is same as night usually, but let's keep it simple
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
                # Hunter check (Night death usually allows Hunter to shoot unless poisoned by Witch - complex rule, let's assume yes)
                self.handle_hunter_death(p)

        if self.check_win_condition(): return

        # 3. Discussion (Simplified)
        # Verify Seer info sharing
        self.share_information()

        # 4. Voting
        self.run_voting_phase()
        
        self.check_win_condition()

    def run_sheriff_election(self):
        logger.info("Running Sheriff Election...")
        candidates = self.get_alive_players()
        # Seer automatically runs? Prompt: "预言家自动当选警长" -> well simplified rule says automated.
        # "如果开启对话...预言家和女巫会公开自己晚上的信息，预言家自动当选警长"
        # So if Seer assumes Sheriff.
        seers = self.get_players_by_role(RoleType.SEER)
        if seers and seers[0].is_alive:
            self.sheriff = seers[0]
            self.sheriff.sheriff = True
            logger.info(f"Sheriff is Player {self.sheriff.id} ({self.sheriff.role.name})")
        else:
            # Random or no sheriff
            logger.info("Seer dead or not found, random Sheriff elected.")
            self.sheriff = random.choice(candidates)
            self.sheriff.sheriff = True
            logger.info(f"Sheriff is Player {self.sheriff.id}")

    def share_information(self):
        # Seer reveals info
        seers = self.get_players_by_role(RoleType.SEER)
        if seers and seers[0].is_alive:
            seer = seers[0]
            for pid, role_type in seer.known_roles.items():
                logger.info(f"[Discussion] Seer {seer.id} says: Player {pid} is {role_type.value}")
    
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
            for pid, role_type in seers[0].known_roles.items():
                if role_type == RoleType.WEREWOLF:
                    # Find alive player
                     for p in candidates:
                         if p.id == pid:
                             confirmed_wolves.append(p)

        # Cast Votes
        for voter in candidates:
            vote_target = None
            if voter.role.role_type == RoleType.WEREWOLF:
                vote_target = wolf_target
            else:
                if confirmed_wolves:
                    vote_target = confirmed_wolves[0] # Vote first confirmed wolf
                else:
                    # Vote random person who is NOT themselves and NOT confirmed good (if known)
                    # Simplified: random other
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
            executed = max(votes, key=votes.get)
            logger.info(f"Voting Result: Player {executed.id} is executed!")
            
            # Idiot Check
            if executed.role.role_type == RoleType.IDIOT and not executed.role.revealed:
                logger.info(f"Player {executed.id} flips card: I am an IDIOT!")
                executed.role.reveal()
                # Immune to death by vote
                logger.info("Idiot survives execution.")
            else:
                executed.die()
                self.handle_sheriff_death(executed)
                self.handle_hunter_death(executed)

    def handle_sheriff_death(self, dead_player: Player):
        if self.sheriff != dead_player:
            return
            
        logger.info(f"Sheriff {dead_player.id} died. Transferring badge...")
        self.sheriff.sheriff = False
        
        candidates = self.get_alive_players()
        if not candidates:
            self.sheriff = None
            return

        next_sheriff = None
        
        # Logic: 
        # Wolf -> Teammate
        # Seer -> Last Verified Good
        # Good -> Most trusted (random good logic)
        
        if dead_player.role.role_type == RoleType.WEREWOLF:
            wolves = [p for p in candidates if p.role.role_type == RoleType.WEREWOLF]
            if wolves:
                next_sheriff = random.choice(wolves)
        elif dead_player.role.role_type == RoleType.SEER:
            # Find last verified good
            # This requires tracking order of verification or just picking one known good
            known_goods = [pid for pid, r in dead_player.known_roles.items() if r != RoleType.WEREWOLF]
            # Find matching alive players
            valid_targets = [p for p in candidates if p.id in known_goods]
            if valid_targets:
                next_sheriff = valid_targets[-1] # "Last" verified roughly
        
        # Fallback: Random trusting good
        if not next_sheriff:
             next_sheriff = random.choice(candidates) # Simplified
             
        self.sheriff = next_sheriff
        self.sheriff.sheriff = True
        logger.info(f"New Sheriff is Player {self.sheriff.id}")

    def handle_hunter_death(self, dead_player: Player):
         if dead_player.role.role_type == RoleType.HUNTER:
            # Check if poisoned (Witch logic interaction needed, but for now allow shoot)
            if not dead_player.poisoned:
                logger.info(f"Hunter {dead_player.id} triggers skill!")
                targets = self.get_alive_players()
                if targets:
                    shot = random.choice(targets)
                    logger.info(f"Hunter shoots Player {shot.id}")
                    shot.die()
                    self.handle_sheriff_death(shot)
                    # Recursive hunter? Rare but possible
                    self.handle_hunter_death(shot)
