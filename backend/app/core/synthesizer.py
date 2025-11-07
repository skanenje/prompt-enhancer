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

    def infer_field(self, field_name: str, prompt: str, field_description: str = "") -> str:
        """Use AI models to intelligently infer field values from prompt context"""
        
        # Create inference prompt for the AI model
        inference_prompt = f"""
Analyze this user prompt and extract the most appropriate value for the '{field_name}' field.

User prompt: "{prompt}"
Field to extract: {field_name}
Field description: {field_description}

Provide only the extracted value, no explanation. Keep it concise and relevant to the prompt context.
If the field cannot be determined from the prompt, provide a reasonable default.
"""
        
        # Try Gemini first for better inference
        if self.gemini_model:
            try:
                response = self.gemini_model.generate_content(inference_prompt)
                result = response.text.strip()
                if result and len(result) < 200:  # Reasonable length check
                    return result
            except Exception:
                pass
        
        # Fallback to T5 model
        if self.enhancer:
            try:
                result = self.enhancer(f"Extract {field_name} from: {prompt}", max_length=50, do_sample=False)
                if result and result[0]['generated_text']:
                    return result[0]['generated_text'].strip()
            except Exception:
                pass
        
        # Final fallback: simple extraction
        return self._simple_field_extraction(field_name, prompt)
    
    def _simple_field_extraction(self, field_name: str, prompt: str) -> str:
        """Simple fallback extraction when AI models are unavailable"""
        field_lower = field_name.lower()
        prompt_lower = prompt.lower()
        
        # Basic topic extraction
        topic_patterns = [
            r"(?:about|learn about|understand|explain)\s+(.+?)(?:\s+(?:that|which|for|to)|[.!?]|$)",
            r"(?:what is|tell me about)\s+(.+?)(?:[.!?]|$)"
        ]
        
        topic = ""
        for pattern in topic_patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                topic = match.group(1).strip()
                break
        
        # Field-specific defaults with topic context
        defaults = {
            "action": f"Explain {topic}" if topic else "Provide information",
            "purpose": f"to understand {topic}" if topic else "to get information",
            "context": f"Learning about {topic}" if topic else "General inquiry",
            "expectation": "Clear and comprehensive explanation",
            "role": "knowledgeable expert",
            "audience": "someone seeking to learn",
            "tone": "informative and helpful",
            "length": "detailed" if "detailed" in prompt_lower else "comprehensive",
            "objective": f"teaching about {topic}" if topic else "providing education",
            "task": f"explain {topic}" if topic else "inform",
            "goal": "comprehensive understanding",
            "situation": f"Need to understand {topic}" if topic else "Learning context"
        }
        
        return defaults.get(field_lower, topic or "relevant information")

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
        import logging
        logger = logging.getLogger(__name__)
        
        overrides = overrides or {}
        diag = []
        template = framework.get("template", "")
        fields_spec = framework.get("fields", {})
        
        logger.debug(f"📋 Template: {template}")
        logger.debug(f"📝 Fields to fill: {list(fields_spec.keys())}")
        
        # Build mapping to fill
        fill_map = {}
        for field_name in fields_spec.keys():
            if field_name in overrides and overrides[field_name]:
                fill_map[field_name] = overrides[field_name]
                diag.append(f"Using override for {field_name}: '{overrides[field_name]}'")
                logger.debug(f"⚙️ Override {field_name}: '{overrides[field_name]}'")
            else:
                field_desc = fields_spec.get(field_name, {}).get("description", "")
                inferred = self.infer_field(field_name, prompt, field_desc)
                fill_map[field_name] = inferred
                logger.debug(f"🧠 AI-inferred {field_name}: '{inferred}'")
                if inferred:
                    diag.append(f"AI-inferred {field_name}: '{inferred}'")
                else:
                    diag.append(f"No value for {field_name}; left blank")

        logger.debug(f"🗺 Fill map: {fill_map}")
        
        # Fill template
        try:
            raw = template.format(**fill_map)
            logger.debug(f"✅ Template filled successfully: '{raw}'")
        except Exception as e:
            logger.debug(f"⚠️ Template fill failed: {e}")
            parts = [f"{k}: {v}" for k,v in fill_map.items() if v]
            raw = prompt + " " + " ".join(parts)
            logger.debug(f"🔄 Fallback raw: '{raw}'")

        # Naturalize
        naturalized = self.naturalize(raw)
        logger.debug(f"🌿 Naturalized: '{naturalized}'")
        
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
        logger.debug(f"🏁 Final result: '{final}'")
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
