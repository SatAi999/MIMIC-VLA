from typing import List, Dict, Any

class TaskDecomposer:
    def decompose(self, intent_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        intent_type = intent_data.get("intent")
        
        if intent_type == "emergency_rescue":
            return [
                {"step": 1, "action": "FIND", "target": "victim_01", "description": "Locate injured person"},
                {"step": 2, "action": "FIND", "target": "medical_kit_01", "description": "Locate medical kit"},
                {"step": 3, "action": "PLAN_SAFE_ROUTE", "target": "medical_kit_01", "description": "Evaluate route risk to medical kit"},
                {"step": 4, "action": "NAVIGATE", "target": "medical_kit_01", "description": "Navigate to medical kit"},
                {"step": 5, "action": "PICK", "target": "medical_kit_01", "description": "Retrieve medical kit"},
                {"step": 6, "action": "PLAN_SAFE_ROUTE", "target": "victim_01", "description": "Evaluate route risk to victim"},
                {"step": 7, "action": "NAVIGATE", "target": "victim_01", "description": "Navigate to victim"},
                {"step": 8, "action": "DELIVER", "item": "medical_kit_01", "target": "victim_01", "description": "Hand over medical kit to victim"},
                {"step": 9, "action": "VERIFY", "task": "delivery", "description": "Verify medical kit delivery"}
            ]
        elif intent_type == "hydration_assistance":
            return [
                {"step": 1, "action": "GROUND_SEMANTIC", "query": "drinkable item", "description": "Find beverage"},
                {"step": 2, "action": "NAVIGATE", "target": "water_bottle_01", "description": "Navigate to bottle"},
                {"step": 3, "action": "PICK", "target": "water_bottle_01", "description": "Pick up water bottle"},
                {"step": 4, "action": "NAVIGATE", "target": "user", "description": "Navigate to user"},
                {"step": 5, "action": "DELIVER", "item": "water_bottle_01", "target": "user", "description": "Deliver drink"},
                {"step": 6, "action": "VERIFY", "task": "delivery", "description": "Verify hydration delivery"}
            ]
        elif intent_type == "semantic_retrieval":
            return [
                {"step": 1, "action": "GROUND_SEMANTIC", "query": "writing tool", "description": "Ground writing instrument"},
                {"step": 2, "action": "NAVIGATE", "target": "pen_01", "description": "Navigate to pen"},
                {"step": 3, "action": "PICK", "target": "pen_01", "description": "Pick pen"},
                {"step": 4, "action": "DELIVER", "item": "pen_01", "target": "user", "description": "Bring pen to user"},
                {"step": 5, "action": "VERIFY", "task": "retrieval", "description": "Verify retrieval"}
            ]
        else:
            return [
                {"step": 1, "action": "SEARCH", "target": "area", "description": "Scan environment"},
                {"step": 2, "action": "REPORT", "target": "status", "description": "Report observations"}
            ]
