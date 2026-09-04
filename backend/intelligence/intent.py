from typing import Dict, Any

class IntentParser:
    def __init__(self):
        pass

    def parse(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        
        if "injured" in text_lower or "medical" in text_lower or "rescue" in text_lower:
            return {
                "raw_text": text,
                "intent": "emergency_rescue",
                "goal": "deliver_medical_kit_to_victim",
                "priority": "HIGH",
                "target_entity": "victim_01",
                "item_entity": "medical_kit_01",
                "supported": True
            }
        elif "thirsty" in text_lower or "drink" in text_lower:
            return {
                "raw_text": text,
                "intent": "hydration_assistance",
                "goal": "retrieve_drinkable_item",
                "priority": "MEDIUM",
                "target_entity": "user",
                "item_entity": "water_bottle_01",
                "supported": True
            }
        elif "write" in text_lower or "pen" in text_lower:
            return {
                "raw_text": text,
                "intent": "semantic_retrieval",
                "goal": "retrieve_writing_tool",
                "priority": "MEDIUM",
                "target_entity": "user",
                "item_entity": "pen_01",
                "supported": True
            }
        elif "warehouse" in text_lower or "package" in text_lower:
            return {
                "raw_text": text,
                "intent": "warehouse_dispatch",
                "goal": "dispatch_package",
                "priority": "HIGH",
                "target_entity": "dispatch_zone",
                "item_entity": "package_patna",
                "supported": True
            }
        else:
            return {
                "raw_text": text,
                "intent": "unsupported_command",
                "goal": "request_clarification",
                "priority": "NONE",
                "target_entity": None,
                "item_entity": None,
                "supported": False,
                "message": "UNCERTAIN / REQUEST CLARIFICATION: Unrecognized natural language intent."
            }
