"""
Claw Engine Bridge
------------------
This module bridges the Claw Engine (ported Claude Code internals)
with the Omni-MNC Super Brain.

The Claw Engine provides:
- Smart prompt routing (PortRuntime)
- Multi-turn conversation memory (QueryEnginePort)
- Session persistence (SessionStore)
- Tool permission control (ToolPermissionContext)
- History logging (HistoryLog)
- Cost tracking (CostTracker)
"""

import sys
import os

# Add claw_engine to Python path
CLAW_ENGINE_PATH = os.path.join(os.path.dirname(__file__), "claw_engine")
if CLAW_ENGINE_PATH not in sys.path:
    sys.path.insert(0, CLAW_ENGINE_PATH)

try:
    from src.runtime import PortRuntime
    from src.query_engine import QueryEnginePort
    from src.session_store import load_session
    from src.history import HistoryLog
    from src.permissions import ToolPermissionContext
    from src.tool_pool import assemble_tool_pool
    CLAW_ENGINE_AVAILABLE = True
    print("[Claw Engine] ✅ All modules loaded successfully.")
except Exception as e:
    CLAW_ENGINE_AVAILABLE = False
    print(f"[Claw Engine] ⚠️ Could not load: {e}")


class ClawEngineBridge:
    """
    Bridge between the Omni-MNC Super Brain and the Claw Engine.
    Provides smart routing, memory, and session management.
    """

    def __init__(self):
        self.available = CLAW_ENGINE_AVAILABLE
        if self.available:
            self.runtime = PortRuntime()
            self.history = HistoryLog()
            print("[Claw Bridge] ✅ Bridge initialized.")
        else:
            self.runtime = None
            self.history = None
            print("[Claw Bridge] ⚠️ Running without Claw Engine.")

    def route(self, prompt: str, limit: int = 5) -> list:
        """
        Use the Claw Engine's smart router to find the best
        command/tool matches for a given prompt.
        """
        if not self.available:
            return []
        try:
            matches = self.runtime.route_prompt(prompt, limit=limit)
            self.history.add("route", f"prompt={prompt!r} matches={len(matches)}")
            return matches
        except Exception as e:
            print(f"[Claw Bridge] Route error: {e}")
            return []

    def bootstrap_session(self, prompt: str) -> str:
        """
        Run a full bootstrap session with the Claw Engine.
        Returns a markdown report of the session.
        """
        if not self.available:
            return "Claw Engine not available."
        try:
            session = self.runtime.bootstrap_session(prompt)
            return session.as_markdown()
        except Exception as e:
            return f"Session error: {e}"

    def run_turn_loop(self, prompt: str, max_turns: int = 3) -> list:
        """
        Run a multi-turn conversation loop using the Claw Engine.
        This enables multi-step reasoning chains.
        """
        if not self.available:
            return []
        try:
            results = self.runtime.run_turn_loop(prompt, max_turns=max_turns)
            return [r.output for r in results]
        except Exception as e:
            print(f"[Claw Bridge] Turn loop error: {e}")
            return []


# Singleton bridge instance
CLAW_BRIDGE = ClawEngineBridge()
