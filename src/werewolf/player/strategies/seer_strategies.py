from werewolf.game.game import Game
from werewolf.player.player import Player
import random
from typing import Any, Dict, List
from .base_strategies import BasicStrategy

class SeerBasicStrategy(BasicStrategy):

    def _update_sheriff_flow(self, player: 'Player', game_state: 'Game'):
        alive_others = [p.player_id for p in game_state.get_alive_players() if p.player_id != player.player_id]
        unverified = [pid for pid in alive_others if pid not in self.memory.get("verified", {})]
        
        current_flow = self.memory.get("sheriff_flow", [])
        # 保留依然存活且未查验的
        current_flow = [pid for pid in current_flow if pid in unverified]
        
        # 补充到两个
        while len(current_flow) < 2 and len(unverified) > len(current_flow):
            candidates = [pid for pid in unverified if pid not in current_flow]
            if candidates:
                current_flow.append(random.choice(candidates))
            else:
                break
                
        self.memory["sheriff_flow"] = current_flow

    def receive_night_feedback(self, player: 'Player', result: Any):
        if result and "target" in result and "is_werewolf" in result:
            if "verified" not in self.memory:
                self.memory["verified"] = {}
            self.memory["verified"][result["target"]] = result["is_werewolf"]
            self.memory["last_result"] = result

    

    def act_night(self, player: 'Player', game_state: 'Game') -> Any:
        self._update_sheriff_flow(player, game_state)
        flow = self.memory.get("sheriff_flow", [])
        if flow:
            target = flow.pop(0)
            self.memory["sheriff_flow"] = flow
        else:
            alive_others = [p.player_id for p in game_state.get_alive_players() if p.player_id != player.player_id]
            unverified = [p for p in alive_others if p not in self.memory.get("verified", {})]
            target = random.choice(unverified) if unverified else (random.choice(alive_others) if alive_others else None)
        
        self.memory["last_check"] = target
        return target

    def elect_sheriff_strategy(self, player: 'Player', game_state: 'Game') -> bool:
        return True

    def vote_sheriff(self, player: 'Player', game_state: 'Game', targets: List[int]) -> int:
        last_res = self.memory.get("last_result")
        if last_res and not last_res["is_werewolf"] and last_res["target"] in targets:
            return last_res["target"]
            
        known_wolves = [pid for pid, is_wolf in self.memory.get("verified", {}).items() if is_wolf]
        valid_targets = [t for t in targets if t not in known_wolves]
        return random.choice(valid_targets) if valid_targets else (random.choice(targets) if targets else None)

    def transfer_sheriff_strategy(self, player: 'Player', game_state: 'Game') -> int:
        alive_others = [p.player_id for p in game_state.get_alive_players() if p.player_id != player.player_id]
        if not alive_others:
            return None
            
        last_res = self.memory.get("last_result")
        if last_res and not last_res["is_werewolf"] and last_res["target"] in alive_others:
            return last_res["target"]
            
        verified = self.memory.get("verified", {})
        good_guys = [pid for pid, is_wolf in verified.items() if not is_wolf and pid in alive_others]
        if good_guys:
            return random.choice(good_guys)
            
        for role in ["witch", "hunter", "idiot"]:
            candidates = [pid for pid in alive_others if self.belief.get(pid, {}).get(f"is_{role}") == 1.0]
            if candidates:
                return random.choice(candidates)
                
        known_wolves = [pid for pid, is_wolf in verified.items() if is_wolf]
        valid_targets = [t for t in alive_others if t not in known_wolves]
        return random.choice(valid_targets) if valid_targets else random.choice(alive_others)

    def last_words_strategy(self, player: 'Player', game_state: 'Game') -> tuple[str, dict]:
        last_res = self.memory.get("last_result")
        claims = {"jump_role": "Seer", "check_kill": [], "gold_water": []}
        if last_res:
            target = last_res["target"]
            if last_res["is_werewolf"]:
                speech = f"我是预言家，昨晚验了 {target} 号，是查杀。"
                claims["check_kill"].append(target)
            else:
                speech = f"我是预言家，昨晚验了 {target} 号，是金水。"
                claims["gold_water"].append(target)
            return speech, claims
        return "我是预言家，没来得及验出结果就死了。", claims

    def speech_day_strategy(self, player: 'Player', game_state: 'Game') -> tuple[str, dict]:
        self._update_sheriff_flow(player, game_state)
        flow = self.memory.get("sheriff_flow", [])
        last_res = self.memory.get("last_result")
        claims = {"jump_role": "Seer", "check_kill": [], "gold_water": [], "sheriff_flow": flow}
        
        speech = "我是预言家。"
        if last_res:
            target = last_res["target"]
            if last_res["is_werewolf"]:
                speech += f"昨晚验了 {target} 号，是查杀！今天全票打飞 {target} 号！"
                claims["check_kill"].append(target)
            else:
                speech += f"昨晚验了 {target} 号，是金水。大家不要出他。"
                claims["gold_water"].append(target)
                
        if flow:
            speech += f" 我的警徽流依次是 {flow}。"
            
        self.memory.pop("last_result", None)
        return speech, claims

    def vote_day_strategy(self, player: 'Player', game_state: 'Game') -> int:
        alive_others = [p.player_id for p in game_state.get_alive_players() if p.player_id != player.player_id]
        if not alive_others:
            return None
            
        verified = self.memory.get("verified", {})
        known_wolves = [pid for pid, is_wolf in verified.items() if is_wolf and pid in alive_others]
        
        if known_wolves:
            return random.choice(known_wolves)
            
        known_goods = [pid for pid, is_wolf in verified.items() if not is_wolf and pid in alive_others]
        unknowns = [pid for pid in alive_others if pid not in known_wolves and pid not in known_goods]
        
        return random.choice(unknowns) if unknowns else random.choice(alive_others)
