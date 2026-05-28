from werewolf.game.game import Game
from werewolf.player.player import Player
import random
from typing import Any, Dict, List, Tuple
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
            candidates = [pid for pid in alive_others if player.belief_state.get(pid, {}).get(f"is_{role}") == 1.0]
            if candidates:
                return random.choice(candidates)
                
        known_wolves = [pid for pid, is_wolf in verified.items() if is_wolf]
        valid_targets = [t for t in alive_others if t not in known_wolves]
        return random.choice(valid_targets) if valid_targets else random.choice(alive_others)

    def last_words_strategy(self, player: 'Player', game_state: 'Game') -> tuple[str, dict]:
        last_res = self.memory.get("last_result")
        claims = {"jump_role": "Seer", "check_kill": [], "gold_water": [], "called_vote_target":None}
        if last_res:
            target = last_res["target"]
            target_info = self.decide_vote_target(player, game_state)
            vote_target = target_info[0] if isinstance(target_info, tuple) else target_info
            claims["called_vote_target"] = vote_target
            self.memory["called_vote_target"] = vote_target
            if last_res["is_werewolf"]:
                speech = f"我是预言家，昨晚验了 {target} 号，是查杀。"
                claims["check_kill"].append(target)
            else:
                speech = f"我是预言家，昨晚验了 {target} 号，是金水。"
                claims["gold_water"].append(target)
            if vote_target:
                speech += f"我建议大家今天把 {vote_target} 号投出去。"
            return speech, claims
        return "我是预言家，没来得及验出结果就死了。", claims



    def speech_day_strategy(self, player: 'Player', game_state: 'Game') -> tuple[str, dict]:
        self._update_sheriff_flow(player, game_state)
        flow = self.memory.get("sheriff_flow", [])
        last_res = self.memory.get("last_result")
        claims = {
            "jump_role": "Seer", 
            "check_kill": [], 
            "gold_water": [], 
            "sheriff_flow": flow,
            "called_vote_target":None
        }
        
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
        
        target_info = self.decide_vote_target(player, game_state)
        vote_target = target_info[0] if isinstance(target_info, tuple) else target_info
        claims["called_vote_target"] = vote_target
        self.memory["called_vote_target"] = vote_target
        if vote_target:
            speech += f" 我建议大家今天把 {vote_target} 号投出去。"
            
        self.memory.pop("last_result", None)
        return speech, claims

    def update_belief_after_speech(self, player: 'Player', speaker_id: int, speech: str, claims: Dict[str, Any], game_state: 'Game'):
        self.update_belief_after_last_words(player, speaker_id, speech, claims, game_state)

    def vote_day_strategy(self, player: 'Player', game_state: 'Game') -> Tuple[int, str]:
        alive_others = [p.player_id for p in game_state.get_alive_players() if p.player_id != player.player_id]
        called_target = self.memory.get("called_vote_target")
        if called_target in alive_others:
            return called_target, "坚持自己号召的目标"
        return self.decide_vote_target(player, game_state)

    def decide_vote_target(self, player: 'Player', game_state: 'Game') -> Tuple[int, str]:
        alive_others = [p.player_id for p in game_state.get_alive_players() if p.player_id != player.player_id]
        if not alive_others:
            return None, "没有其他人存活"
            
        verified = self.memory.get("verified", {})
        known_wolves = [pid for pid, is_wolf in verified.items() if is_wolf and pid in alive_others]
        
        if known_wolves:
            return random.choice(known_wolves), "投给已知的狼人"
            
        known_goods = [pid for pid, is_wolf in verified.items() if not is_wolf and pid in alive_others]
        flow = self.memory.get("sheriff_flow", [])
        avoid = set(known_goods + flow)
        
        unknowns = [pid for pid in alive_others if pid not in known_wolves and pid not in avoid]
        
        if unknowns:
            return random.choice(unknowns), "在未知身份且不在警徽流的人中随机投"
            
        # 如果除开警徽流没别人了，就在除开已知好人的人里面投
        remaining = [pid for pid in alive_others if pid not in known_wolves and pid not in known_goods]
        if remaining:
            return random.choice(remaining), "迫于无奈在警徽流的人里随机投"
            
        return random.choice(alive_others), "走投无路随机投"
