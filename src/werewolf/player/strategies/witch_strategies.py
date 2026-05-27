import random
from typing import Any
from .base_strategies import BaseRandomStrategy

class WitchRandomStrategy(BaseRandomStrategy):
    def act_night(self, player: 'Player', game_state: 'Game') -> Any:
        alive_others = [p.player_id for p in game_state.get_alive_players() if p.player_id != player.player_id]
        action = {}
        if player.role.has_antidote and game_state.current_wolf_kill:
            # 女巫救人概率调高点以便测试
            if random.random() < 0.8:
                action["save"] = True
                self.memory["last_save_target"] = game_state.current_wolf_kill
                return action
        if player.role.has_poison and alive_others:
            if random.random() < 0.3:
                action["poison"] = random.choice(alive_others)
                return action
        return None

    def receive_night_feedback(self, player: 'Player', result: Any):
        if result and result.get("save"):
            self.memory["saved_player"] = self.memory.get("last_save_target")

    def speech_day_strategy(self, player: 'Player', game_state: 'Game') -> tuple[str, dict]:
        claims = {"jump_role": "Witch", "silver_water": None}
        saved = self.memory.get("saved_player")
        if saved and not self.memory.get("has_claimed_silver_water"):
            self.memory["has_claimed_silver_water"] = True
            claims["silver_water"] = saved
            return f"我是女巫，昨晚我救了 {saved} 号，他是我的银水。", claims
            
        return "我是好人，目前还不清楚局势，过。", {}
