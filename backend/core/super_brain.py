"""
Omni-MNC Super Brain v2.0
==========================
The Central AI Routing Engine for the Omni-MNC.
Now powered by:
  - Claw Engine (Claude Code internals) for smart routing & memory
  - Multi-provider Fallback Chain (5 AI providers)
  - Semantic JSON intent detection
  - Full session history & memory
"""

import os
import sys
import json
import random
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# ─── Claw Engine Integration ───────────────────────────────────────────────────
CLAW_ENGINE_PATH = os.path.join(os.path.dirname(__file__), "claw_engine")
if CLAW_ENGINE_PATH not in sys.path:
    sys.path.insert(0, CLAW_ENGINE_PATH)

try:
    from src.runtime import PortRuntime
    from src.history import HistoryLog
    from src.session_store import load_session
    CLAW_AVAILABLE = True
except Exception as e:
    CLAW_AVAILABLE = False
    print(f"[Super Brain] Claw Engine not loaded: {e}")

# ─── Provider Definitions ──────────────────────────────────────────────────────
PROVIDERS = {
    "groq": {
        "key_env": "GROQ_API_KEY",
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "llama-3.1-8b-instant",
    },
    "openrouter": {
        "key_env": "OPENROUTER_API_KEY",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "model": "google/gemma-4-31b-it:free",
    },
    "mistral": {
        "key_env": "MISTRAL_API_KEY",
        "url": "https://api.mistral.ai/v1/chat/completions",
        "model": "mistral-small-latest",
    },
    "cohere": {
        "key_env": "COHERE_API_KEY",
        "url": None,  # Uses cohere SDK
        "model": "command-r",
    },
    "together": {
        "key_env": "TOGETHER_API_KEY",
        "url": "https://api.together.xyz/v1/chat/completions",
        "model": "meta-llama/Llama-3-8b-chat-hf",
    },
}


# ─── Agent Specialization Models ──────────────────────────────────────────────
AGENT_MODELS = {
    "Super Brain": ("openrouter", "meta-llama/llama-3.3-70b-instruct:free"),
    "Campaign Manager": ("openrouter", "meta-llama/llama-3.3-70b-instruct:free"),
    "Chief Architect": ("openrouter", "qwen/qwen-2.5-coder-32b-instruct:free"),
    "Coder Agent": ("openrouter", "qwen/qwen-2.5-coder-32b-instruct:free"),
    "QA Agent": ("openrouter", "qwen/qwen-2.5-coder-32b-instruct:free"),
    "DevOps Agent": ("openrouter", "meta-llama/llama-3-8b-instruct:free"),
    "Security Agent": ("groq", "llama-3.1-8b-instant"),
    "Research Agent": ("openrouter", "meta-llama/llama-3-8b-instruct:free"),
    "Copywriter Agent": ("openrouter", "google/gemma-4-31b-it:free"),
    "Art Director Agent": ("openrouter", "google/gemma-4-31b-it:free"),
    "Graphic Engine Agent": ("groq", "llama-3.1-8b-instant"),
    "Social Media Agent": ("openrouter", "google/gemma-4-31b-it:free"),
    "Email Agent": ("openrouter", "meta-llama/llama-3-8b-instruct:free"),
    "Calendar Agent": ("openrouter", "meta-llama/llama-3-8b-instruct:free"),
    "Comms Agent": ("groq", "llama-3.1-8b-instant"),
    "Finance Agent": ("openrouter", "meta-llama/llama-3-8b-instruct:free"),
    "Legal Agent": ("openrouter", "meta-llama/llama-3.3-70b-instruct:free"),
    "Memory Agent": ("openrouter", "meta-llama/llama-3-8b-instruct:free"),
    "Retrieval Agent": ("openrouter", "meta-llama/llama-3-8b-instruct:free"),
    "Analytics Agent": ("openrouter", "meta-llama/llama-3-8b-instruct:free"),
}


class SuperBrain:
    """
    The Omni-MNC Super Brain v2.0
    - Multi-provider Fallback Chain (never goes offline)
    - Claw Engine routing & memory
    - Semantic JSON intent detection
    - Full conversation history
    """

    def __init__(self):
        # Load all API keys
        self.api_keys = {
            name: os.getenv(cfg["key_env"])
            for name, cfg in PROVIDERS.items()
        }

        # Build ordered fallback chain (skip providers with no key)
        self.fallback_chain = [
            name for name in ["groq", "openrouter", "mistral", "together", "cohere"]
            if self.api_keys.get(name)
        ]

        print(f"[Super Brain] ACTIVE providers: {self.fallback_chain}")

        # Claw Engine for smart routing & memory
        if CLAW_AVAILABLE:
            self.claw_runtime = PortRuntime()
            self.history = HistoryLog()
            print("[Super Brain] Claw Engine routing & memory active.")
        else:
            self.claw_runtime = None
            self.history = None

    # ─── Core Fallback Chain ───────────────────────────────────────────────────

    def _call_provider(self, provider: str, prompt: str, model_override: str = None) -> str:
        """Call a single provider. Returns response text or raises Exception."""
        cfg = PROVIDERS[provider]
        key = self.api_keys.get(provider)
        if not key:
            raise ValueError(f"No key for {provider}")

        model = model_override if model_override else cfg["model"]

        if provider == "cohere":
            import cohere
            co = cohere.Client(key)
            resp = co.chat(message=prompt, model=model)
            return resp.text

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        resp = requests.post(cfg["url"], headers=headers, json=data, timeout=30)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        raise Exception(f"HTTP {resp.status_code}: {resp.text[:200]}")

    def think(self, prompt: str, agent_name: str = None) -> Dict[str, Any]:
        """
        The MAIN method. Runs the Fallback Chain.
        Tries each provider in order until one succeeds.
        If agent_name is specified, attempts their customized agent model first.
        """
        # Determine initial provider and model based on agent_name
        initial_provider = None
        initial_model = None
        if agent_name and agent_name in AGENT_MODELS:
            initial_provider, initial_model = AGENT_MODELS[agent_name]

        # Use Claw Engine routing if available
        claw_context = ""
        if self.claw_runtime:
            try:
                matches = self.claw_runtime.route_prompt(prompt, limit=3)
                if matches:
                    claw_context = f"\n[Claw Route: {', '.join(m.name for m in matches)}]"
            except Exception:
                pass

        # 1. Try agent's primary custom model first
        if initial_provider and self.api_keys.get(initial_provider):
            try:
                print(f"[Super Brain] Trying custom agent model for {agent_name}: {initial_provider} ({initial_model})")
                response = self._call_provider(initial_provider, prompt, model_override=initial_model)
                if self.history:
                    self.history.add("think", f"agent={agent_name} provider={initial_provider} model={initial_model} prompt={prompt[:50]!r}")
                return {
                    "status": "success",
                    "provider": initial_provider,
                    "model": initial_model,
                    "response": response + claw_context,
                }
            except Exception as e:
                print(f"[Super Brain] Custom agent model failed: {e}. Falling back to default chain.")

        # 2. Fall back to standard fallback chain
        last_error = None
        for provider in self.fallback_chain:
            # Skip if we already tried this provider as the initial_provider
            if provider == initial_provider:
                continue
            try:
                print(f"[Super Brain] Trying provider: {provider}")
                response = self._call_provider(provider, prompt)

                # Log to Claw history
                if self.history:
                    self.history.add("think", f"provider={provider} prompt={prompt[:50]!r}")

                return {
                    "status": "success",
                    "provider": provider,
                    "model": PROVIDERS[provider]["model"],
                    "response": response + claw_context,
                }
            except Exception as e:
                print(f"[Super Brain] {provider} failed: {e}")
                last_error = str(e)
                continue

        # All providers failed
        return {
            "status": "error",
            "provider": "none",
            "model": "none",
            "response": f"[Super Brain] All configured providers failed. Last error: {last_error}. Please add a valid API key.",
        }

    # ─── Intent Detection ──────────────────────────────────────────────────────

    def get_intent(self, directive: str) -> dict:
        """
        Semantic JSON intent detection using the Fallback Chain.
        Returns structured intent: CAMPAIGN, RESEARCH, CODE, CHAT
        """
        prompt = f"""Analyze the following directive and extract the intent.
Return ONLY a valid JSON object. No markdown, no explanation.
Possible intents: CAMPAIGN, RESEARCH, CODE, CHAT.
Format: {{"INTENT": "...", "ENTITY": "..."}}
Directive: "{directive}" """

        result = self.think(prompt, agent_name="Super Brain")
        try:
            clean = result["response"].replace("```json", "").replace("```", "").strip()
            return json.loads(clean)
        except Exception:
            # Smart keyword fallback
            d = directive.lower()
            if any(w in d for w in ["poster", "campaign", "ad", "promotion"]):
                return {"INTENT": "CAMPAIGN", "ENTITY": directive}
            if any(w in d for w in ["research", "analyze", "find", "search"]):
                return {"INTENT": "RESEARCH", "ENTITY": directive}
            if any(w in d for w in ["code", "script", "build", "write", "create"]):
                return {"INTENT": "CODE", "ENTITY": directive}
            return {"INTENT": "CHAT", "ENTITY": "general"}

    # ─── Legacy compatibility ──────────────────────────────────────────────────

    def ask(self, intent: str, context: Dict[str, Any], agent_tier: str) -> Dict[str, Any]:
        """Legacy method for backward compatibility."""
        return self.think(intent)

    def consensus_ask(self, intent: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ask multiple providers and return all responses.
        Best for critical decisions requiring accuracy.
        """
        responses = []
        for provider in self.fallback_chain[:3]:
            try:
                text = self._call_provider(provider, intent)
                responses.append({"provider": provider, "response": text})
            except Exception as e:
                responses.append({"provider": provider, "error": str(e)})

        return {
            "status": "success",
            "mode": "CONSENSUS",
            "providers_used": len(responses),
            "responses": responses,
        }

    def get_status(self) -> Dict[str, Any]:
        """Returns the current health status of the Super Brain."""
        return {
            "active_providers": self.fallback_chain,
            "claw_engine": CLAW_AVAILABLE,
            "total_providers_configured": len([k for k in self.api_keys.values() if k]),
        }


# ─── Global Singleton ──────────────────────────────────────────────────────────
GLOBAL_SUPER_BRAIN = SuperBrain()
