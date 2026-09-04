from typing import List, Dict, Any, Optional

class SemanticGroundingEngine:
    def __init__(self):
        # Semantic mapping knowledge base for zero-shot intent grounding
        self.semantic_taxonomy = {
            "writing_instruments": ["pen", "pencil", "marker", "notebook", "quill", "stylus"],
            "illumination_tools": ["flashlight", "torch", "lamp", "lantern", "phone"],
            "hydration_containers": ["water_bottle", "cup", "bottle", "mug", "flask", "drink"],
            "medical_supplies": ["medical_kit", "first_aid", "bandage", "medicine"],
            "human_targets": ["victim", "person", "human", "patient"]
        }

    def ground_intent(self, intent_text: str, candidate_objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Grounds natural language intent or vague descriptions into the best matching object in the scene.
        """
        intent_lower = intent_text.lower()
        
        # Concept extraction
        target_category = None
        if any(w in intent_lower for w in ["write", "pen", "notes", "pencil", "journal"]):
            target_category = "writing_instruments"
        elif any(w in intent_lower for w in ["dark", "see", "light", "illumination", "flashlight"]):
            target_category = "illumination_tools"
        elif any(w in intent_lower for w in ["thirsty", "drink", "water", "beverage", "cup"]):
            target_category = "hydration_containers"
        elif any(w in intent_lower for w in ["injured", "medical", "first aid", "rescue", "kit"]):
            target_category = "medical_supplies"
            
        target_concepts = self.semantic_taxonomy.get(target_category, [])
        
        best_match = None
        best_score = -1.0
        
        for obj in candidate_objects:
            obj_type = obj.get("type", "").lower()
            confidence = obj.get("confidence", 1.0)
            
            score = 0.0
            if obj_type in target_concepts:
                score = 1.0 * confidence
            elif any(concept in obj_type for concept in target_concepts):
                score = 0.8 * confidence
            else:
                score = 0.05 * confidence
                
            if score > best_score:
                best_score = score
                best_match = obj
                
        return {
            "query": intent_text,
            "matched_object": best_match,
            "confidence": round(best_score, 2),
            "matched_category": target_category or "general_object"
        }
