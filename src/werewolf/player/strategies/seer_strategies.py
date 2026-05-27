import random
from typing import Any
from .base_strategies import BaseRandomStrategy

class SeerRandomStrategy(BaseRandomStrategy):
    def act_night(self, player: 'Player', game_state: 'Game') -> Any:
        alive_others = [p.player_id for p in game_state.get_alive_players() if p.player_id != player.player_id]
        # 不要查验已经查过的人
        unverified = [p for p in alive_others if p not in self.memory.get("verified", {})]
        target = random.choice(unverified) if unverified else (random.choice(alive_others) if alive_others else None)
        self.memory["last_check"] = target
        return target

    def receive_night_feedback(self, player: 'Player', result: Any):
        if result and "target" in result and "is_werewolf" in result:
            if "verified" not in self.memory:
                self.memory["verified"] = {}
            self.memory["verified"][result["target"]] = result["is_werewolf"]
            self.memory["last_result"] = result

    def speech_day_strategy(self, player: 'Player', game_state: 'Game') -> tuple[str, dict]:
        # 如果昨晚验了人，就报出来
        last_result = self.memory.get("last_result")
        claims = {"jump_role": "Seer", "check_kill": [], "gold_water": []}
        
        if last_result:
            target = last_result["target"]
            is_wolf = last_result["is_werewolf"]
            if is_wolf:
                speech = f"我是预言家，昨晚验了 {target} 号，是查杀！今天全票打飞 {target} 号！"
                claims["check_kill"].append(target)
            else:
                speech = f"我是预言家，昨晚验了 {target} 号，是金水。大家不要出他。"
                claims["gold_water"].append(target)
                
            # 清空 last_result 防止明天重复报（简单处理）
            self.memory.pop("last_result", None)
            return speech, claims
            
        return "我是预言家，但我昨晚没验出结果，过。", claims

# class SeerLLMStrategy(BaseLLMStrategy): ...
