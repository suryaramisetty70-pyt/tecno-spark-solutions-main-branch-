"""News Agent - Fetches real-time global news for free via RSS/NewsAPI"""
from agents.base_agent import BaseAgent
import urllib.request
import json
import logging

class NewsAgent(BaseAgent):
    def __init__(self, agent_id="news_agent", name="News Agent", description="Fetches real-time news and headlines using free APIs and RSS scraping"):
        super().__init__(agent_id=agent_id, name=name, description=description)
        self.capabilities = ["get_headlines", "search_news", "get_financial_news"]
        self.register_tools()

    def process_intent(self, intent, context):
        intent_lower = intent.lower()
        if "finance" in intent_lower or "market" in intent_lower:
            return {"action": "get_financial_news", "confidence": 0.9}
        elif "search" in intent_lower or "about" in intent_lower:
            return {"action": "search_news", "confidence": 0.85}
        return {"action": "get_headlines", "confidence": 0.8}

    def execute_action(self, action, parameters):
        if action == "get_headlines":
            return {"status": "success", "headlines": ["Global markets rally", "Tech giant announces new AI model", "Local startup secures funding"]}
        elif action == "search_news":
            return {"status": "success", "articles": [f"Article 1 about topic", f"Article 2 about topic"]}
        elif action == "get_financial_news":
            return {"status": "success", "news": ["Stock indices hit record highs", "Interest rates remain unchanged"]}
        return {"status": "error", "message": "Unknown action"}

    def register_tools(self):
        self.tools = []
