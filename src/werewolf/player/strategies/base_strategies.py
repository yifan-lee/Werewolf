from werewolf.game.game import Game
from werewolf.player.player import Player
import random
from typing import Any, Dict, Tuple, List
from ..strategy import Strategy

class BasicStrategy(Strategy):
    """
    提供随机策略的基础实现，处理所有白天共用的投票、发言逻辑。
    夜晚逻辑 act_night 和复杂的 update_belief 由具体子类重写。
    """
    
    def __init__(self):
        super().__init__()

    def receive_night_feedback(self, player: 'Player', result: Any):
        # 基类不处理具体反馈
        pass

    def act_night(self, player: 'Player', game_state: 'Game') -> Any:
        return None

    def elect_sheriff_strategy(self, player: 'Player', game_state: 'Game') -> bool:
        # 默认不竞选警长
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

    def execute_death_effect(self, player: 'Player', game_state: Any) -> Any:
        # 默认没有特殊效果
        return None

    def transfer_sheriff_strategy(self, player: 'Player', game_state: Any) -> int:
        return self.vote_sheriff(player, game_state, None)

    def last_words_strategy(self, player: 'Player', game_state: 'Game') -> Tuple[str, Dict[str, Any]]:
        return "我是好人，我死得很冤。", {}

    def update_belief_after_last_words(self, player: 'Player', speaker_id: int, last_words: str, claims: Dict[str, Any], game_state: 'Game'):
        if not claims:
            return

        role_claim = claims.get("jump_role")

        if role_claim:
            player.belief_state[speaker_id][f"is_{role_claim.lower()}"] = 1.0

        gold_water = claims.get("gold_water")
        if gold_water is not None:
            for target in claims.get("gold_water", []):
                player.belief_state[target]["is_gold_water"] = 1.0

        silver_water = claims.get("silver_water")
        if silver_water is not None:
            player.belief_state[silver_water]["is_silver_water"] = 1.0

        check_kill = claims.get("check_kill")
        if check_kill is not None:
            for target in claims.get("check_kill", []):
                player.belief_state[target]["is_werewolf"] = 1.0

        called_vote_target = claims.get("called_vote_target")
        if called_vote_target is not None:
            player.belief_state[speaker_id]["latest_called_vote_target"] = called_vote_target

        sheriff_flow = claims.get("sheriff_flow")
        if sheriff_flow is not None:
            player.belief_state[speaker_id]["latest_sheriff_flow"] = sheriff_flow

    def update_belief_after_badge_transfer(self, player: 'Player', dead_sheriff_id: int, new_sheriff_id: int, game_state: 'Game'):
        b = player.belief_state.get(dead_sheriff_id, {})
        if b.get("is_seer") == 1.0:
            if new_sheriff_id is not None:
                if new_sheriff_id not in player.belief_state:
                    player.belief_state[new_sheriff_id] = {}
                player.belief_state[new_sheriff_id]["is_gold_water"] = 1.0
                
                flow = b.get("latest_sheriff_flow", [])
                if len(flow) > 1 and new_sheriff_id == flow[1] and flow[0] in game_state.alive_players:
                    if flow[0] not in player.belief_state:
                        player.belief_state[flow[0]] = {}
                    player.belief_state[flow[0]]["is_werewolf"] = 1.0
            else:
                flow = b.get("latest_sheriff_flow", [])
                alive_flow = [pid for pid in flow if pid in game_state.alive_players]
                if alive_flow:
                    if alive_flow[0] not in player.belief_state:
                        player.belief_state[alive_flow[0]] = {}
                    player.belief_state[alive_flow[0]]["is_werewolf"] = 1.0

    def speech_day_strategy(self, player: 'Player', game_state: 'Game') -> Tuple[str, Dict[str, Any]]:
        claims = {"called_vote_target": None}
        target_info = self.vote_day_strategy(player, game_state)
        target = target_info[0] if isinstance(target_info, tuple) else target_info
        claims["called_vote_target"] = target
        self.memory["called_vote_target"] = target
        if target:
            return f"我是好人，我建议大家把 {target} 号投出去。(来自 {player.role.name} 的发言)", claims
        return f"我是好人，过。(来自 {player.role.name} 的发言)", claims


    def update_belief_after_speech(self, player: 'Player', speaker_id: int, speech: str, claims: Dict[str, Any], game_state: 'Game'):
        self.update_belief_after_last_words(player, speaker_id, speech, claims, game_state)

    def vote_day_strategy(self, player: 'Player', game_state: Any) -> Tuple[int, str]:
        alive_others = [p.player_id for p in game_state.get_alive_players() if p.player_id != player.player_id]
        called_target = self.memory.get("called_vote_target")
        if called_target in alive_others:
            return called_target, "坚持自己号召的目标"
        return self.decide_vote_target(player, game_state)

    def decide_vote_target(self, player: 'Player', game_state: 'Game') -> Tuple[int, str]:
        alive_others = [
            p.player_id for p in game_state.get_alive_players() if p.player_id != player.player_id
        ]
        if not alive_others:
            return None, "没有其他人存活"

        # 1. 自己相信的预言家的 called_vote_target
        for pid in game_state.alive_players:
            if player.belief_state.get(pid, {}).get("is_seer") == 1.0:
                target = player.belief_state.get(pid, {}).get("latest_called_vote_target")
                if target == player.player_id:
                    return pid, f"反咬一口：相信的预言家 {pid} 想要投我，我投他"
                elif target in alive_others:
                    return target, f"跟随相信的预言家 {pid} 的号召"

        # 2. 自己相信的女巫的 called_vote_target
        for pid in game_state.alive_players:
            if player.belief_state.get(pid, {}).get("is_witch") == 1.0:
                target = player.belief_state.get(pid, {}).get("latest_called_vote_target")
                if target == player.player_id:
                    return pid, f"反咬一口：相信的女巫 {pid} 想要投我，我投她"
                elif target in alive_others:
                    return target, f"跟随相信的女巫 {pid} 的号召"

        is_sheriff = (game_state.sheriff_id == player.player_id)

        # 4. 如果1，2都没有claim，自己不是警长，就选警长当天发言的claim里面的called_vote_target
        if not is_sheriff and game_state.sheriff_id in game_state.alive_players:
            sheriff_target = player.belief_state.get(game_state.sheriff_id, {}).get("latest_called_vote_target")
            if sheriff_target == player.player_id:
                return game_state.sheriff_id, f"反咬一口：警长 {game_state.sheriff_id} 想要投我，我投他"
            elif sheriff_target in alive_others:
                return sheriff_target, f"跟随警长 {game_state.sheriff_id} 的号召"

        # 3. 如果1，2都没有claim，自己还是警长（或者没警长），就按原来的逻辑选一个，尽量避开金水和银水
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

        

    ### Support functions

    def get_score(self, player: 'Player', pid: int) -> float:
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
        elif b.get("is_werewolf") == 1.0:
            score -= 1000
        else:
            # 给一个基础分加上随机波动，确保其他好人之间随机杀
            score += random.random() * 10 
        return score