from typing import Dict, Any, List
from backend.rl.config import rl_config
from backend.rl.action_space import ACTION_NAMES, RLAction

class DecisionFusionEngine:
    def __init__(self):
        pass

    def fuse_decisions(
        self,
        planner_candidate: Dict[str, Any],
        rl_recommendation: Dict[str, Any],
        learned_risk: float,
        memory_prior: float,
        safety_check_fn: Any = None
    ) -> Dict[str, Any]:
        """
        Fuses deterministic planner, RL policy recommendations, learned risk, and safety filters.
        Enforces fallback to planner if RL confidence is below threshold (<0.65) or action is evaluated unsafe.
        """
        planner_action_name = planner_candidate.get("name", "Route B") if planner_candidate else "NO_SAFE_ROUTE"
        rl_action_int = rl_recommendation.get("action", 0)
        rl_action_name = rl_recommendation.get("action_name", "CONTINUE_CURRENT_ROUTE")
        rl_confidence = rl_recommendation.get("confidence", 0.0)

        use_rl = False
        selected_action = planner_action_name
        selection_reason = "Planner optimal safe route selected"

        if rl_config.rl_enabled and rl_confidence >= rl_config.rl_confidence_threshold:
            if rl_action_int in [RLAction.TAKE_ALTERNATE_ROUTE, RLAction.REPLAN]:
                use_rl = True
                selected_action = "Route C (RL Recommended Detour)"
                selection_reason = f"RL Policy ({rl_recommendation['source']}) recommended {rl_action_name} (Conf: {rl_confidence*100:.0f}%)"

        # Hard Safety Gate check filter
        safety_status = "APPROVED"
        if safety_check_fn and use_rl:
            # Validate RL recommendation through Safety Gate check
            is_safe = safety_check_fn(selected_action)
            if not is_safe:
                safety_status = "REJECTED_BY_SAFETY_GATE"
                use_rl = False
                selected_action = planner_action_name
                selection_reason = f"RL recommendation rejected by Safety Gate. Fallback to Planner: {planner_action_name}"

        return {
            "planner_action": planner_action_name,
            "rl_action": rl_action_name,
            "rl_confidence": rl_confidence,
            "learned_risk": learned_risk,
            "memory_prior": memory_prior,
            "selected_action": selected_action,
            "selection_reason": selection_reason,
            "used_rl": use_rl,
            "safety_status": safety_status
        }
