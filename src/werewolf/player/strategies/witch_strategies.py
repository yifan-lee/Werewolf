from werewolf.game.game import Game
from werewolf.player.player import Player
import random
from typing import Any, List, Tuple, Dict
from .base_strategies import BasicStrategy

class WitchBasicStrategy(BasicStrategy):
    def act_night(self, player: 'Player', game_state: 'Game') -> Any:
        alive_others = [p.player_id for p in game_state.get_alive_players() if p.player_id != player.player_id]
        action = {}
        
        # 1.1 & 1.3 如果有解药且有人死亡，100% 使用解药
        if player.role.has_antidote and game_state.current_wolf_kill:
            action["save"] = True
            self.memory["last_save_target"] = game_state.current_wolf_kill
            return action
            
        # 1.2 & 1.3 如果解药没有使用，且有毒药，立刻使用毒药
        # 优先毒杀认为是狼人的玩家 (即 get_score 最低的玩家)
        if player.role.has_poison and alive_others:
            scores = {pid: self.get_score(pid) for pid in alive_others}
            min_score = min(scores.values())
            suspects = [pid for pid, s in scores.items() if s == min_score]
            action["poison"] = random.choice(suspects)
            return action
            
        return None

    def receive_night_feedback(self, player: 'Player', result: Any):
        if result and result.get("save"):
            self.memory["saved_player"] = self.memory.get("last_save_target")

    def elect_sheriff_strategy(self, player: 'Player', game_state: 'Game') -> bool:
        return False

    def vote_sheriff(self, player: 'Player', game_state: 'Game', targets: List[int]) -> int:
        if not targets:
            targets = [
                p.player_id for p in game_state.get_alive_players() if p.player_id != player.player_id
            ]
        scores = {pid: self.get_score(pid) for pid in targets}
        max_score = max(scores.values())
        top_targets = [pid for pid, s in scores.items() if s == max_score]
        return random.choice(top_targets) if top_targets else None

    def transfer_sheriff_strategy(self, player: 'Player', game_state: Any) -> int:
        return self.vote_sheriff(player, game_state, None)

    def last_words_strategy(self, player: 'Player', game_state: 'Game') -> Tuple[str, Dict[str, Any]]:
        claims = {"jump_role": "Witch", "silver_water": None}
        saved = self.memory.get("saved_player")
        if saved and not self.memory.get("has_claimed_silver_water"):
            self.memory["has_claimed_silver_water"] = True
            claims["silver_water"] = saved
            return f"我是女巫，昨晚我救了 {saved} 号，他是我的银水。", claims
        return "我是女巫，还没救人，过。", {}

    def update_belief_after_last_words(self, player: 'Player', speaker_id: int, last_words: str, claims: Dict[str, Any], game_state: 'Game'):
        if not claims:
            return

        if speaker_id not in self.belief:
            self.belief[speaker_id] = {}
            
        role_claim = claims.get("jump_role")

        if role_claim:
            self.belief[speaker_id][f"is_{role_claim.lower()}"] = 1.0

        gold_water = claims.get("gold_water")
        if gold_water is not None:
            for target in claims.get("gold_water", []):
                if target not in self.belief:
                    self.belief[target] = {}
                self.belief[target]["is_gold_water"] = 1.0
   
        
    def speech_day_strategy(self, player: 'Player', game_state: 'Game') -> tuple[str, dict]:
        return self.last_words_strategy(player, game_state) 

    def update_belief_after_speech(self, player: 'Player', speaker_id: int, speech: str, claims: Dict[str, Any], game_state: 'Game'):
        self.update_belief_after_last_words(player, speaker_id, speech, claims, game_state)
        
