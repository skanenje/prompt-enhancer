# backend/app/core/synthesizer.py
from typing import Dict, Tuple, List
from app import loader
import re

try:
    from transformers import pipeline, T5ForConditionalGeneration, T5Tokenizer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

def _clean_whitespace(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

class Synthesizer:
    """
    AI-enhanced prompt synthesizer using Hugging Face transformers.
    Fills framework templates and applies semantic enhancement.
    """
    def __init__(self):
        self.enhancer = None
        if TRANSFORMERS_AVAILABLE:
            try:
                # Use a lightweight model for text improvement
                self.enhancer = pipeline("text2text-generation", model="t5-small", max_length=512)
            except Exception:
                pass

    def infer_field(self, field_name: str, prompt: str):
        # Simple heuristics to infer common fields
        l = prompt.lower()
        if field_name.lower() in ["length"]:
            if any(w in l for w in ["short","brief","one paragraph","tweet","subject"]):
                return "short"
            return "medium"
        if field_name.lower() in ["emotion","tone"]:
            if any(w in l for w in ["urgent","asap","immediately"]):
                return "urgent"
            if any(w in l for w in ["fun","casual","playful"]):
                return "casual"
            return "neutral"
        if field_name.lower() in ["context","situation","goal","purpose","task"]:
            # return a concise restatement
            return prompt.strip()
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
        if self.enhancer and len(naturalized.split()) > 5:
            try:
                enhanced = self._ai_enhance(naturalized)
                if enhanced and len(enhanced) > len(naturalized) * 0.7:  # Quality check
                    final = enhanced
                    diag.append("Applied AI enhancement")
                else:
                    final = naturalized
                    diag.append("Used naturalized version (AI enhancement failed quality check)")
            except Exception:
                final = naturalized
                diag.append("AI enhancement failed, using naturalized version")
        else:
            final = naturalized
            if explain:
                diag.append("Naturalized final prompt")
        
        final = re.sub(r"Given\s*,\s*", "", final)
        final = _clean_whitespace(final)
        return final, diag
    
    def _ai_enhance(self, text: str) -> str:
        """Use T5 to improve prompt clarity and structure"""
        enhancement_prompt = f"Improve this prompt for clarity and specificity: {text}"
        result = self.enhancer(enhancement_prompt, max_length=len(text.split()) + 50, do_sample=False)
        return result[0]['generated_text'] if result else text
