import requests
import json
import logging
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        # STRICT REQUIREMENT: v1 endpoint, gemini-2.5-flash model (Verified Available)
        self.url = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent"
        
        self.system_instructions = """You are a Legal Information Assistant.
You explain laws, rights, and legal procedures in simple language.
You do NOT provide legal advice, predictions, or guarantees.
You assist users by explaining concepts, risks, options, and procedures.
You always include a disclaimer for case-related questions.
You adapt responses to the user’s language and education level."""

    def _call_gemini(self, prompt_text: str, language: str = None) -> str:
        # Construct payload with system instructions prepended to user prompt
        lang_instruction = f"\n\nIMPORTANT: Provide the response in {language} language." if language else ""
        full_text = f"{self.system_instructions}\n\n{prompt_text}{lang_instruction}"
        
        payload = {
            "contents": [
                {
                    "parts": [{"text": full_text}]
                }
            ]
        }
        
        # Retry Logic: backoff factor for 429 server errors
        retries = 3
        backoff = 2  # initial wait seconds

        for attempt in range(retries):
            try:
                logger.info(f"Calling Gemini API: {self.url} (Attempt {attempt+1}/{retries})")
                response = requests.post(
                    f"{self.url}?key={self.api_key}", 
                    json=payload, 
                    timeout=30
                )
                
                # Check for 429 specific error and retry
                if response.status_code == 429:
                    if attempt < retries - 1:
                        logger.warning(f"Rate limit hit (429). Retrying in {backoff} seconds...")
                        import time
                        time.sleep(backoff)
                        backoff *= 2  # Exponential backoff
                        continue
                    else:
                        # Final failure after retries
                        return "⚠️ The AI service is temporarily unavailable. Please try again later."
                
                response.raise_for_status()
                data = response.json()
                
                if "candidates" in data and len(data["candidates"]) > 0:
                    content = data["candidates"][0].get("content", {})
                    parts = content.get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
                
                return "Error: Empty response from AI."
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Gemini API Request Error: {e}")
                
                # Retry on 429 if caught as exception
                if hasattr(e, 'response') and e.response is not None and e.response.status_code == 429:
                     if attempt < retries - 1:
                        logger.warning(f"Rate limit hit (429). Retrying in {backoff} seconds...")
                        import time
                        time.sleep(backoff)
                        backoff *= 2
                        continue
                     else:
                        return "⚠️ The AI service is temporarily unavailable. Please try again later."

                # For any other error, return generic message instead of raw JSON
                return "⚠️ The AI service is temporarily unavailable. Please try again later."
        
        return "⚠️ The AI service is temporarily unavailable. Please try again later."

    def get_legal_explanation(self, query: str, language: str = None) -> str:
        prompt = f"User Query: {query}\n\nExplain this law or legal concept in simple terms."
        return self._call_gemini(prompt, language=language)

    def analyze_document(self, text: str, doc_type: str = "generic", language: str = None) -> str:
        prompt = f"""I have a document (Type: {doc_type}) with the following content:

{text[:90000]}

Please analyze this legal document and provide strategic insights.
Identify:
1. Case Summary & Key Facts
2. Relevant Legal Sections & Laws
3. **Strengths of the Case**: Points that favor the winning of this case.
4. **Weaknesses/Risks**: Areas that need attention.
5. **Strategic Suggestions**: Legal steps or evidence that could help strengthen the position.
6. **Next Procedural Steps**: What typically happens next.

Provide the response in simple, clear language with bullet points.
Disclaimer: State clearly that this is an analysis for informational purposes only.
"""
        return self._call_gemini(prompt, language=language)
