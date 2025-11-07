# backend/app/core/evaluator.py
from typing import Tuple, List, Dict
import re

class Evaluator:
    """
    Simple scoring heuristics:
    - clarity: presence of an explicit action verb
    - specificity: presence of numbers, timeframe, audience
    - completeness: required fields present is handled upstream; here we check length
    """
    def __init__(self):
        pass

    def score(self, enhanced_prompt: str, framework: Dict, parsed: Dict) -> Tuple[float, List[str]]:
        notes = []
        score = 0.0
        text = enhanced_prompt.lower()
        # clarity — look for verbs
        if re.search(r"\b(explain|design|create|summarize|generate|write|compare|analyze|recommend)\b", text):
            score += 3.0
            notes.append("Contains clear action verb.")
        else:
            notes.append("Missing explicit action verb.")
        # specificity — numbers, timeframe, audience
        if re.search(r"\b\d+\b", text):
            score += 2.0
            notes.append("Contains numeric specificity.")
        if any(w in text for w in ["audience","audiences","marketing","student","developer","clinician","engineer","manager"]):
            score += 1.5
            notes.append("Mentions audience.")
        # length bonus
        if len(text.split()) > 6:
            score += 1.0
        # tone score
        if parsed.get("tone") and parsed.get("tone") != "neutral" and parsed.get("tone") in text:
            score += 0.5
        # normalize to 0-10 roughly
        final = min(10.0, score)
        return final, notes
