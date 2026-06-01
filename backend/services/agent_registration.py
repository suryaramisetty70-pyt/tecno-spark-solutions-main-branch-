"""
Agent Registration Service
Auto-registers all agents into marketplace on startup
"""
import os
import json
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def auto_register_agents():
    """Automatically register all agents in the agents directory"""
    try:
        from backend.services.marketplace_service import marketplace_service

        agents_dir = Path("backend/agents")
        registered_count = 0

        # Find all agent config files
        config_files = list(agents_dir.glob("*_config.json"))
        logger.info(f"Found {len(config_files)} agent configurations")

        for config_file in config_files:
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)

                # Register agent in marketplace
                marketplace_service.register_agent(config)
                registered_count += 1

            except Exception as e:
                logger.warning(f"Failed to register agent {config_file}: {e}")

        logger.info(f"Registered {registered_count} agents in marketplace")
        return registered_count

    except Exception as e:
        logger.error(f"Agent registration failed: {e}")
        return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    auto_register_agents()
