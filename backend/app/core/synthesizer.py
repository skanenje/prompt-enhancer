# backend/app/core/synthesizer.py
from typing import Dict, Tuple, List
from app import loader
import re

def _clean_whitespace(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

class Synthesizer:
    """
    Fills a framework template with provided or inferred fields,
    then naturalizes the text (removes leftover placeholders elegantly)
    """
    def __init__(self):
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

        # Attempt to fill template placeholders like {Context}
        try:
            raw = template.format(**fill_map)
        except Exception:
            # fallback: append sentences
            parts = [f"{k}: {v}" for k,v in fill_map.items() if v]
            raw = prompt + " " + " ".join(parts)

        # naturalize
        final = self.naturalize(raw)
        # Optionally, if final still literal like "Given , write..." clean more heuristics:
        final = re.sub(r"Given\s*,\s*", "", final)
        final = _clean_whitespace(final)
        if explain:
            diag.append("Naturalized final prompt.")
        return final, diag
