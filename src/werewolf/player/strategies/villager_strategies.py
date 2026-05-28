from werewolf.game.game import Game
from werewolf.player.player import Player
import random
from typing import Any, Dict
from .base_strategies import BasicStrategy

class VillagerBasicStrategy(BasicStrategy):
    def update_belief_after_speech(self, player: 'Player', speaker_id: int, speech: str, claims: Dict[str, Any], game_state: 'Game'):
        if not claims:
            return
            
        # 非常基础的启发式认知模型
        if speaker_id not in self.belief:
            self.belief[speaker_id] = {"prob_seer": 0.0, "prob_wolf": 0.0}
            
        if claims.get("jump_role") == "Seer":
            # 有人跳预言家，平民暂时给他一点信任
            self.belief[speaker_id]["prob_seer"] += 0.4
            
            for target in claims.get("check_kill", []):
                if target not in self.belief:
                    self.belief[target] = {"prob_seer": 0.0, "prob_wolf": 0.0}
                # 如果我相信他是预言家，那么他发查杀的人大概率是狼
                self.belief[target]["prob_wolf"] += 0.4 * self.belief[speaker_id]["prob_seer"]
                
            for target in claims.get("gold_water", []):
                if target not in self.belief:
                    self.belief[target] = {"prob_seer": 0.0, "prob_wolf": 0.0}
                # 他发金水的人大概率是好人
                self.belief[target]["prob_wolf"] = max(0.0, self.belief[target]["prob_wolf"] - 0.4)

    def vote_day_strategy(self, player: 'Player', game_state: 'Game') -> int:
        alive_others = [p.player_id for p in game_state.get_alive_players() if p.player_id != player.player_id]
        if not alive_others:
            return None
            
        # 寻找嫌疑最大的人
        suspects = [
            (pid, self.belief.get(pid, {}).get("prob_wolf", 0.0))
            for pid in alive_others
        ]
        # 挑出 prob_wolf 最高的，如果有多个，随机选一个
        max_prob = max([prob for pid, prob in suspects] + [0.0])
        if max_prob > 0.0:
            top_suspects = [pid for pid, prob in suspects if prob == max_prob]
            return random.choice(top_suspects)
        
        # 否则随便投
        return random.choice(alive_others)

# 以后可以加入:
# class VillagerLLMStrategy(BaseLLMStrategy): ...
