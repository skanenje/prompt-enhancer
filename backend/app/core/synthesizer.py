# backend/app/core/synthesizer.py
from typing import Dict, Tuple, List
from app import loader
import re

try:
    from transformers import pipeline, T5ForConditionalGeneration, T5Tokenizer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

def _clean_whitespace(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

class Synthesizer:
    """
    AI-enhanced prompt synthesizer using Hugging Face transformers.
    Fills framework templates and applies semantic enhancement.
    """
    def __init__(self):
        self.enhancer = None
        self.gemini_model = None
        
        # Try Gemini first (better results)
        if GEMINI_AVAILABLE:
            try:
                # Configure with API key from environment
                import os
                api_key = os.getenv('GEMINI_API_KEY')
                if api_key:
                    genai.configure(api_key=api_key)
                    self.gemini_model = genai.GenerativeModel('gemini-pro')
            except Exception:
                pass
        
        # Fallback to local transformers
        if TRANSFORMERS_AVAILABLE and not self.gemini_model:
            try:
                self.enhancer = pipeline("text2text-generation", model="t5-small", max_length=512)
            except Exception:
                pass

    def infer_field(self, field_name: str, prompt: str):
        l = prompt.lower()
        field_lower = field_name.lower()
        
        # Length inference
        if field_lower == "length":
            if any(w in l for w in ["short","brief","paragraph","tweet"]):
                return "short"
            return "detailed explanation"
        
        # Tone/Emotion inference
        if field_lower in ["emotion","tone"]:
            if any(w in l for w in ["urgent","asap","immediately"]):
                return "urgent"
            if any(w in l for w in ["fun","casual","playful"]):
                return "casual"
            return "informative"
        
        # Action inference
        if field_lower == "action":
            if "learn" in l:
                return "Explain in detail"
            if "understand" in l:
                return "Break down and clarify"
            return "Provide comprehensive information"
        
        # Purpose inference
        if field_lower == "purpose":
            if "learn" in l:
                return "to gain knowledge and understanding"
            if "understand" in l:
                return "to comprehend the concepts"
            return "to get informed"
        
        # Expectation inference
        if field_lower == "expectation":
            if "learn" in l or "understand" in l:
                return "Clear explanations with examples"
            return "Comprehensive and accurate information"
        
        # Context/Situation - extract key topic
        if field_lower in ["context", "situation"]:
            # Extract main topic after common phrases
            topic_match = re.search(r"(?:about|learn about|understand)\s+(.+?)(?:\s+that|$)", l)
            if topic_match:
                return f"Learning about {topic_match.group(1).strip()}"
            return "Educational inquiry"
        
        # Task inference
        if field_lower == "task":
            if "learn" in l:
                topic_match = re.search(r"learn about\s+(.+?)(?:\s+that|$)", l)
                if topic_match:
                    return f"learn about {topic_match.group(1).strip()}"
            return "understand the topic"
        
        # Goal inference
        if field_lower == "goal":
            return "gain comprehensive understanding"
        
        # Audience inference
        if field_lower == "audience":
            return "someone wanting to learn"
        
        # Role inference
        if field_lower == "role":
            return "knowledgeable instructor"
        
        return ""

    def naturalize(self, raw_template: str) -> str:
        # Remove placeholders left empty: patterns like " {Field}" or " to achieve {Result}."
        # Approach: remove substrings with empty braces and tidy connectors.
        s = raw_template
        # remove leftover braces (if any)
        s = re.sub(r"\{[^\}]*\}", "", s)
        # clean repeated commas/spaces/connectors
        s = re.sub(r"\s+[,\.]\s+", ". ", s)
        s = re.sub(r"\s+and\s+to\s+achieve\s+\.\s*", ".", s, flags=re.IGNORECASE)
        s = _clean_whitespace(s)
        # Ensure punctuation at end
        if not s.endswith("."):
            s = s + "."
        return s

    def synthesize(self, prompt: str, framework: Dict, overrides: Dict[str,str] = None, explain: bool = False) -> Tuple[str, List[str]]:
        overrides = overrides or {}
        diag = []
        template = framework.get("template", "")
        fields_spec = framework.get("fields", {})
        
        # Build mapping to fill
        fill_map = {}
        for field_name in fields_spec.keys():
            if field_name in overrides and overrides[field_name]:
                fill_map[field_name] = overrides[field_name]
                diag.append(f"Using override for {field_name}: '{overrides[field_name]}'")
            else:
                inferred = self.infer_field(field_name, prompt)
                fill_map[field_name] = inferred
                if inferred:
                    diag.append(f"Inferred {field_name}: '{inferred}'")
                else:
                    diag.append(f"No value for {field_name}; left blank")

        # Fill template
        try:
            raw = template.format(**fill_map)
        except Exception:
            parts = [f"{k}: {v}" for k,v in fill_map.items() if v]
            raw = prompt + " " + " ".join(parts)

        # Naturalize
        naturalized = self.naturalize(raw)
        
        # AI enhancement if available
        if (self.gemini_model or self.enhancer) and len(naturalized.split()) > 5:
            try:
                enhanced = self._ai_enhance(naturalized)
                if enhanced and len(enhanced) > len(naturalized) * 0.5:  # Quality check
                    final = enhanced
                    diag.append("Applied AI enhancement")
                else:
                    final = naturalized
                    diag.append("Used naturalized version (AI enhancement failed quality check)")
            except Exception as e:
                final = naturalized
                diag.append(f"AI enhancement failed: {str(e)[:50]}...")
        else:
            final = naturalized
            if explain:
                diag.append("Naturalized final prompt")
        
        final = re.sub(r"Given\s*,\s*", "", final)
        final = _clean_whitespace(final)
        return final, diag
    
    def _ai_enhance(self, text: str) -> str:
        """Use Gemini or T5 to improve prompt clarity and structure"""
        enhancement_prompt = f"Improve this prompt for clarity and specificity while keeping the same intent: {text}"
        
        # Try Gemini first
        if self.gemini_model:
            try:
                response = self.gemini_model.generate_content(enhancement_prompt)
                return response.text.strip()
            except Exception:
                pass
        
        # Fallback to T5
        if self.enhancer:
            result = self.enhancer(enhancement_prompt, max_length=len(text.split()) + 50, do_sample=False)
            return result[0]['generated_text'] if result else text
        
        return text
