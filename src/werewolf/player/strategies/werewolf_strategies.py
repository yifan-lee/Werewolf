from werewolf.game.game import Game
from werewolf.player.player import Player
import random
from typing import Any, Dict, List, Tuple
from .base_strategies import BasicStrategy
from ...constants import Faction

class WerewolfBasicStrategy(BasicStrategy):

    def act_night(self, player: 'Player', game_state: 'Game') -> Any:
        alive_non_wolves = [
            p.player_id for p in game_state.get_alive_players() 
            if p.role.faction != Faction.WEREWOLF
        ]
        
        if not alive_non_wolves:
            return None
            
        def get_kill_score(pid: int) -> float:
            b = player.belief_state.get(pid, {})
            score = 0.0
            # 优先级：预言家(1000) > 金水(800) > 女巫(600) > 银水(500) > 白痴(400) > 猎人(200) > 其他(0)
            if b.get("is_seer") == 1.0:
                score += 1000
            elif b.get("is_gold_water") == 1.0:
                score += 800
            elif b.get("is_witch") == 1.0:
                score += 600
            elif b.get("is_silver_water") == 1.0:
                score += 500
            elif b.get("is_idiot") == 1.0:
                score += 400
            elif b.get("is_hunter") == 1.0:
                score += 200
            else:
                # 给一个基础分加上随机波动，确保其他好人之间随机杀
                score += random.random() * 10 
            return score
            
        scores = {pid: get_kill_score(pid) for pid in alive_non_wolves}
        max_score = max(scores.values())
        top_targets = [pid for pid, s in scores.items() if s == max_score]
        
        return random.choice(top_targets) if top_targets else random.choice(alive_non_wolves)

    def elect_sheriff_strategy(self, player: 'Player', game_state: 'Game') -> bool:
        return False


    def update_belief_after_last_words(self, player: 'Player', speaker_id: int, last_words: str, claims: Dict[str, Any], game_state: 'Game'):
        if game_state.players[speaker_id].role.faction == Faction.WEREWOLF:
            return
        if not claims:
            return
            
        wolves = [p.player_id for p in game_state.get_alive_players() if p.role.faction == Faction.WEREWOLF]
        
        role_claim = claims.get("jump_role")
        if role_claim == "Seer":
            # 检查预言家说的对不对
            is_correct = True
            has_info = False
            for target in claims.get("check_kill", []):
                has_info = True
                if target not in wolves:
                    is_correct = False
                    
            for target in claims.get("gold_water", []):
                has_info = True
                if target in wolves:
                    is_correct = False
            
            if has_info:
                if is_correct:
                    player.belief_state[speaker_id]["is_seer"] = 1.0
                    # 既然是真预言家，把他的金水也记下来
                    for target in claims.get("gold_water", []):
                        player.belief_state[target]["is_gold_water"] = 1.0
                else:
                    player.belief_state[speaker_id]["is_seer"] = 0.0
        elif role_claim:
            # 跳其他身份
            player.belief_state[speaker_id][f"is_{role_claim.lower()}"] = 1.0
            
        silver_water = claims.get("silver_water")
        if silver_water is not None:
            player.belief_state[silver_water]["is_silver_water"] = 1.0

        called_vote_target = claims.get("called_vote_target")
        if called_vote_target is not None:
            player.belief_state[speaker_id]["latest_called_vote_target"] = called_vote_target

    def update_belief_after_speech(self, player: 'Player', speaker_id: int, speech: str, claims: Dict[str, Any], game_state: 'Game'):
        self.update_belief_after_last_words(player, speaker_id, speech, claims, game_state)

    def vote_day_strategy(self, player: 'Player', game_state: Any) -> Tuple[int, str]:
        alive_others = [p.player_id for p in game_state.get_alive_players() if p.player_id != player.player_id]
        called_target = self.memory.get("called_vote_target")
        if called_target in alive_others:
            return called_target, "坚持自己号召的目标"
        return self.decide_vote_target(player, game_state)

    def decide_vote_target(self, player: 'Player', game_state: 'Game') -> Tuple[int, str]:
        alive_others = [p.player_id for p in game_state.get_alive_players() if p.player_id != player.player_id]
        if not alive_others:
            return None, "没有其他人存活"

        # 1. 自己相信的预言家的 called_vote_target
        for pid in game_state.alive_players:
            if player.belief_state.get(pid, {}).get("is_seer") == 1.0:
                target = player.belief_state.get(pid, {}).get("latest_called_vote_target")
                if target == player.player_id:
                    # 如果目标是自己，并且自己是狼，那就不会投狼队友，而是反咬预言家
                    return pid, f"反咬一口：相信的预言家 {pid} 想要投我，我投他"
                elif target in alive_others:
                    # 狼人：如果预言家想投的人是我的狼队友，我绝对不跟！
                    if player.belief_state.get(target, {}).get("is_werewolf") == 1.0:
                        continue
                    return target, f"跟随相信的预言家 {pid} 的号召"

        # 2. 自己相信的女巫的 called_vote_target
        for pid in game_state.alive_players:
            if player.belief_state.get(pid, {}).get("is_witch") == 1.0:
                target = player.belief_state.get(pid, {}).get("latest_called_vote_target")
                if target == player.player_id:
                    return pid, f"反咬一口：相信的女巫 {pid} 想要投我，我投她"
                elif target in alive_others:
                    if player.belief_state.get(target, {}).get("is_werewolf") == 1.0:
                        continue
                    return target, f"跟随相信的女巫 {pid} 的号召"

        is_sheriff = (game_state.sheriff_id == player.player_id)

        # 4. 如果1，2都没有claim，自己不是警长，就选警长当天发言的claim里面的called_vote_target
        if not is_sheriff and game_state.sheriff_id in game_state.alive_players:
            sheriff_target = player.belief_state.get(game_state.sheriff_id, {}).get("latest_called_vote_target")
            if sheriff_target == player.player_id:
                return game_state.sheriff_id, f"反咬一口：警长 {game_state.sheriff_id} 想要投我，我投他"
            elif sheriff_target in alive_others:
                if player.belief_state.get(sheriff_target, {}).get("is_werewolf") != 1.0:
                    return sheriff_target, f"跟随警长 {game_state.sheriff_id} 的号召"

        # 3. 如果1，2都没有claim，自己还是警长（或者没警长），就按原来的逻辑选一个
        scores = {pid: -self.get_score(player, pid) for pid in alive_others}
        
        # 狼人绝不投狼人（把已知狼人分数降到极低，或者直接过滤）
        filtered_others = [pid for pid in alive_others if player.belief_state.get(pid, {}).get("is_werewolf") != 1.0]
        if not filtered_others:
            filtered_others = alive_others # 走投无路只能投队友
            
        scores = {pid: -self.get_score(player, pid) for pid in filtered_others}
        max_score = max(scores.values())
        top_targets = [pid for pid, s in scores.items() if s == max_score]
        return random.choice(top_targets), "根据认知评分做出的常规决策"

# 以后这里可以加入:
# class WerewolfLLMStrategy(BaseLLMStrategy): ...
