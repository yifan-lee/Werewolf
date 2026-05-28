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
            scores = {pid: self.get_score(player, pid) for pid in alive_others}
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
        scores = {pid: self.get_score(player, pid) for pid in targets}
        max_score = max(scores.values())
        top_targets = [pid for pid, s in scores.items() if s == max_score]
        return random.choice(top_targets) if top_targets else None

    def transfer_sheriff_strategy(self, player: 'Player', game_state: Any) -> int:
        return self.vote_sheriff(player, game_state, None)

    def last_words_strategy(self, player: 'Player', game_state: 'Game') -> Tuple[str, Dict[str, Any]]:
        claims = {"jump_role": "Witch", "silver_water": None, "called_vote_target": None}
        saved = self.memory.get("saved_player")
        target_info = self.decide_vote_target(player, game_state)
        vote_target = target_info[0] if isinstance(target_info, tuple) else target_info
        claims["called_vote_target"] = vote_target
        self.memory["called_vote_target"] = vote_target
        
        speech = ""
        if saved and not self.memory.get("has_claimed_silver_water"):
            self.memory["has_claimed_silver_water"] = True
            claims["silver_water"] = saved
            speech = f"我是女巫，昨晚我救了 {saved} 号，他是我的银水。"
        else:
            speech = "我是女巫，还没救人，过。"
            
        if vote_target:
            speech += f" 我建议大家今天把 {vote_target} 号投出去。"
            
        return speech, claims


   
        
    def speech_day_strategy(self, player: 'Player', game_state: 'Game') -> tuple[str, dict]:
        return self.last_words_strategy(player, game_state) 

    def update_belief_after_speech(self, player: 'Player', speaker_id: int, speech: str, claims: Dict[str, Any], game_state: 'Game'):
        self.update_belief_after_last_words(player, speaker_id, speech, claims, game_state)
        
    def decide_vote_target(self, player: 'Player', game_state: 'Game') -> Tuple[int, str]:
        alive_others = [p.player_id for p in game_state.get_alive_players() if p.player_id != player.player_id]
        if not alive_others:
            return None, "没有其他人存活"

        # 1. 优先跟随预言家的 called_vote_target
        for pid in game_state.alive_players:
            if player.belief_state.get(pid, {}).get("is_seer") == 1.0:
                target = player.belief_state.get(pid, {}).get("latest_called_vote_target")
                if target == player.player_id:
                    return pid, f"反咬一口：相信的预言家 {pid} 想要投我，我投他"
                elif target in alive_others:
                    return target, f"跟随相信的预言家 {pid} 的号召"

        # 2. 其次投自己觉得最像狼人的（即分数最低的，过滤掉金水银水）
        filtered_others = [
            pid for pid in alive_others 
            if player.belief_state.get(pid, {}).get("is_gold_water") != 1.0 
            and player.belief_state.get(pid, {}).get("is_silver_water") != 1.0
        ]
        if not filtered_others:
            filtered_others = alive_others
            
        scores = {pid: -self.get_score(player, pid) for pid in filtered_others}
        max_score = max(scores.values())
        top_targets = [pid for pid, s in scores.items() if s == max_score]
        return random.choice(top_targets), "根据认知评分做出的常规决策"
