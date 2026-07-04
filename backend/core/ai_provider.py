import httpx
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

class AIProvider:
    """Universal AI Provider for fast, free cloud LLMs (Gemini/Groq)"""

    def __init__(self):
        self.provider = settings.DEFAULT_AI_PROVIDER.lower()
        self.model = settings.DEFAULT_AI_MODEL
        self.gemini_key = settings.GEMINI_API_KEY
        self.groq_key = settings.GROQ_API_KEY
        self.openrouter_key = settings.OPENROUTER_API_KEY
        self.client = httpx.AsyncClient(timeout=30.0)

    async def generate_response(self, system_prompt: str, user_prompt: str, model_id: str = None) -> str:
        """Generate a response using the configured AI provider"""
        
        try:
            if self.provider == "gemini":
                return await self._call_gemini(system_prompt, user_prompt, model_id)
            elif self.provider == "groq":
                return await self._call_groq(system_prompt, user_prompt, model_id)
            elif self.provider == "openrouter":
                return await self._call_openrouter(system_prompt, user_prompt, model_id)
            else:
                logger.warning(f"Unknown provider '{self.provider}', falling back to Groq")
                return await self._call_groq(system_prompt, user_prompt, model_id)
                
        except Exception as e:
            logger.error(f"AI Provider Error ({self.provider}): {e}")
            return f"I encountered an error connecting to my AI brain ({self.provider}). Please check the API keys in the .env file. Error: {str(e)}"

    async def _call_gemini(self, system_prompt: str, user_prompt: str, model_id: str = None) -> str:
        """Call Google Gemini API via REST"""
        if not self.gemini_key:
            return "GEMINI_API_KEY is missing in your .env file. Please add a free key from Google AI Studio."

        active_model = model_id or self.model
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{active_model}:generateContent?key={self.gemini_key}"
        
        payload = {
            "system_instruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": [
                {
                    "parts": [{"text": user_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.9,
                "maxOutputTokens": 1024
            }
        }
        
        response = await self.client.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            return f"Unexpected response format from Gemini: {data}"

    async def _call_groq(self, system_prompt: str, user_prompt: str, model_id: str = None) -> str:
        """Call Groq API (OpenAI compatible) via REST"""
        if not self.groq_key:
            return "GROQ_API_KEY is missing in your .env file. Please add a free key from Groq Console."

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json"
        }
        
        active_model = model_id or self.model
        payload = {
            "model": active_model if active_model != "gemini-1.5-flash" else "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        response = await self.client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            return f"Unexpected response format from Groq: {data}"
            
    async def _call_openrouter(self, system_prompt: str, user_prompt: str, model_id: str = None) -> str:
        """Call OpenRouter API via REST"""
        if not self.openrouter_key:
            return "OPENROUTER_API_KEY is missing in your .env file."

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "HTTP-Referer": "http://localhost:3000",
            "Content-Type": "application/json"
        }
        
        active_model = model_id or self.model
        payload = {
            "model": active_model if active_model not in ["gemini-1.5-flash", "llama3-8b-8192"] else "meta-llama/llama-3-8b-instruct:free",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }
        
        response = await self.client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            return f"Unexpected response format from OpenRouter: {data}"

    async def close(self):
        await self.client.aclose()
