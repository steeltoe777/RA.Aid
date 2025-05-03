import threading
from typing import Dict, Any

from ra_aid.agent_utils import logger

# Global registry mapping session_id -> { thread, stop_event }
agent_thread_registry: Dict[int, Dict[str, Any]] = {}

def stop_agent(session_id: int) -> bool:
    logger.info(f"Requested to stop agent for session_id {session_id}")
    entry = agent_thread_registry.get(session_id)
    if entry and "stop_event" in entry:
        entry["stop_event"].set()
        return True
    logger.warning(f"No agent thread found for session_id {session_id}")
    return False

def is_agent_running(session_id: int) -> bool:
    logger.info(f"Checking if agent is running for session_id {session_id}")
    entry = agent_thread_registry.get(session_id)
    return entry and entry["thread"].is_alive()
