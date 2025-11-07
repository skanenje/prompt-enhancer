# backend/app/core/evaluator.py
from typing import Tuple, List, Dict
import re

class Evaluator:
    """
    Multi-dimensional quality scoring system:
    - clarity: explicit action verbs and clear intent
    - specificity: concrete details, numbers, constraints
    - context_richness: background information and parameters
    - actionability: clear steps and measurable outcomes
    """
    def __init__(self):
        self.action_verbs = {"explain", "design", "create", "summarize", "generate", "write", "compare", "analyze", "recommend", "build", "develop", "implement"}
        self.context_indicators = {"because", "since", "given", "considering", "context", "background", "situation"}
        self.specificity_patterns = [r"\b\d+\b", r"\b(daily|weekly|monthly|annually)\b", r"\b(before|after|by|until)\b"]
    
    def score(self, enhanced_prompt: str, framework: Dict, parsed: Dict) -> Tuple[Dict[str, float], List[str]]:
        text = enhanced_prompt.lower()
        notes = []
        
        clarity = self._score_clarity(text, notes)
        specificity = self._score_specificity(text, notes)
        context_richness = self._score_context_richness(text, parsed, notes)
        actionability = self._score_actionability(text, notes)
        
        overall = (clarity + specificity + context_richness + actionability) / 4
        
        return {
            "clarity": round(clarity, 2),
            "specificity": round(specificity, 2),
            "context_richness": round(context_richness, 2),
            "actionability": round(actionability, 2),
            "overall": round(overall, 2)
        }, notes
    
    def _score_clarity(self, text: str, notes: List[str]) -> float:
        score = 0.0
        
        if any(verb in text for verb in self.action_verbs):
            score += 4.0
            notes.append("Contains clear action verb")
        else:
            notes.append("Missing explicit action verb")
        
        sentences = text.split('.')
        if len(sentences) > 1 and len(sentences) < 5:
            score += 2.0
            notes.append("Well-structured sentences")
        
        ambiguous = ["something", "anything", "maybe", "perhaps", "might"]
        if not any(word in text for word in ambiguous):
            score += 2.0
        else:
            notes.append("Contains ambiguous language")
        
        if text.count('?') <= 1:
            score += 2.0
        
        return min(10.0, score)
    
    def _score_specificity(self, text: str, notes: List[str]) -> float:
        score = 0.0
        
        if re.search(r"\b\d+\b", text):
            score += 3.0
            notes.append("Contains numeric specificity")
        
        if any(re.search(pattern, text) for pattern in self.specificity_patterns[1:]):
            score += 2.0
            notes.append("Includes time constraints")
        
        audiences = ["audience", "user", "student", "developer", "manager", "customer"]
        if any(aud in text for aud in audiences):
            score += 2.0
            notes.append("Specifies target audience")
        
        formats = ["format", "style", "tone", "length", "bullet", "paragraph"]
        if any(fmt in text for fmt in formats):
            score += 2.0
            notes.append("Includes format requirements")
        
        if len([w for w in text.split() if len(w) > 8]) > 2:
            score += 1.0
            notes.append("Contains domain-specific terminology")
        
        return min(10.0, score)
    
    def _score_context_richness(self, text: str, parsed: Dict, notes: List[str]) -> float:
        score = 0.0
        
        if any(indicator in text for indicator in self.context_indicators):
            score += 3.0
            notes.append("Provides contextual background")
        
        if parsed.get("entities") and len(parsed["entities"]) > 0:
            score += 2.0
            notes.append("Contains specific entities")
        
        word_count = len(text.split())
        if word_count > 20:
            score += 2.0
        elif word_count > 10:
            score += 1.0
        
        if parsed.get("subjects") and len(parsed["subjects"]) > 1:
            score += 1.5
        
        if parsed.get("domains") and len(parsed["domains"]) > 0:
            score += 1.5
            notes.append("Demonstrates domain knowledge")
        
        return min(10.0, score)
    
    def _score_actionability(self, text: str, notes: List[str]) -> float:
        score = 0.0
        
        imperatives = ["create", "write", "generate", "build", "design", "develop"]
        if any(imp in text for imp in imperatives):
            score += 3.0
            notes.append("Uses imperative mood")
        
        success_words = ["should", "must", "ensure", "verify", "check", "validate"]
        if any(word in text for word in success_words):
            score += 2.0
            notes.append("Includes success criteria")
        
        measurable = ["measure", "count", "rate", "score", "percentage", "number"]
        if any(word in text for word in measurable):
            score += 2.0
            notes.append("Defines measurable outcomes")
        
        steps = ["first", "then", "next", "finally", "step"]
        if any(step in text for step in steps):
            score += 2.0
            notes.append("Provides step-by-step guidance")
        
        constraints = ["within", "limit", "maximum", "minimum", "constraint"]
        if any(constraint in text for constraint in constraints):
            score += 1.0
        
        return min(10.0, score)
