# AI-Powered Field Inference Setup

## Quick Setup

1. **Get Gemini API Key** (Recommended):
   ```bash
   # Visit https://makersuite.google.com/app/apikey
   # Create API key and copy it
   ```

2. **Configure Environment**:
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run**:
   ```bash
   uvicorn app.main:app --reload
   ```

## How It Works

The system now uses AI models instead of hardcoded rules:

- **Primary**: Gemini API for intelligent field inference
- **Fallback**: Local T5 transformer model
- **Final Fallback**: Simple pattern matching

## Benefits

- ✅ No more hardcoded elif conditions
- ✅ Handles any prompt type intelligently
- ✅ Adapts to new frameworks automatically
- ✅ Better context understanding
- ✅ Scalable to unlimited scenarios

## Example

**Before** (hardcoded):
```python
if field_lower == "action":
    if "learn" in l:
        return "Explain in detail"
    # ... many more elif conditions
```

**After** (AI-powered):
```python
def infer_field(self, field_name: str, prompt: str, field_description: str = ""):
    inference_prompt = f"Extract {field_name} from: {prompt}"
    return self.gemini_model.generate_content(inference_prompt).text
```

The AI model understands context and provides appropriate field values for any scenario.