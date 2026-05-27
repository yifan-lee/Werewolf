import random
from typing import Any, Dict
from .strategy import Strategy
from ..constants import RoleType, Faction

class RandomStrategy(Strategy):
    """一个随机策略基线，展示如何实现各阶段接口"""
    
    def act_night(self, player: 'Player', game_state: 'Game') -> Any:
        alive_others = [p.player_id for p in game_state.get_alive_players() if p.player_id != player.player_id]
        
        if player.role.role_type == RoleType.WEREWOLF:
            # 狼人不能刀自己人
            alive_non_wolves = [p.player_id for p in game_state.get_alive_players() if p.role.faction != Faction.WEREWOLF]
            return random.choice(alive_non_wolves) if alive_non_wolves else None
            
        elif player.role.role_type == RoleType.SEER:
            return random.choice(alive_others) if alive_others else None
            
        elif player.role.role_type == RoleType.WITCH:
            # 随机决定救、毒或不用药
            action = {}
            if player.role.has_antidote and game_state.current_wolf_kill:
                if random.random() < 0.5:
                    action["save"] = True
                    return action
            if player.role.has_poison and alive_others:
                if random.random() < 0.3: # 较低概率盲毒
                    action["poison"] = random.choice(alive_others)
                    return action
            return None
            
        elif player.role.role_type == RoleType.HUNTER:
            # 如果死亡开枪，随机带走一个人
            return random.choice(alive_others) if alive_others else None
            
        return None

    def elect_sheriff_strategy(self, player: 'Player', game_state: 'Game') -> Dict[str, Any]:
        res = {"run_for_sheriff": False, "vote_for": None}
        # 50% 概率上警
        if random.random() < 0.5:
            res["run_for_sheriff"] = True
        else:
            # 不上警则随机投给警上玩家（如果知道的话，这里简化为随机投目前候选人或者不投）
            pass # 简化起见在 game.py 里通过选票决定，具体可在 vote_for 里指定
        return res

    def speech_day_strategy(self, player: 'Player', game_state: 'Game') -> str:
        return "我是好人，过。"

    def last_words_strategy(self, player: 'Player', game_state: 'Game') -> str:
        return "我是好人，我死得很冤。"

    def update_belief_after_speech(self, player: 'Player', speaker_id: int, speech: str, game_state: 'Game'):
        pass

    def update_belief_after_last_words(self, player: 'Player', speaker_id: int, last_words: str, game_state: 'Game'):
        pass

    def vote_day_strategy(self, player: 'Player', game_state: 'Game') -> int:
        alive_others = [p.player_id for p in game_state.get_alive_players() if p.player_id != player.player_id]
        if alive_others:
            # 随便投一个
            return random.choice(alive_others)
        return None

    def transfer_sheriff_strategy(self, player: 'Player', game_state: 'Game') -> int:
        alive_others = [p.player_id for p in game_state.get_alive_players() if p.player_id != player.player_id]
        if alive_others:
            return random.choice(alive_others)
        return None
