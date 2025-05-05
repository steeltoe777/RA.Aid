from typing import Dict, Any
from ra_aid.logging_config import get_logger

logger = get_logger(__name__)

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

def has_received_stop_signal(session_id: int) -> bool:
    logger.info(f"Checking if agent has received stop signal for session_id {session_id}")
    entry = agent_thread_registry.get(session_id)
    return entry and entry["stop_event"].is_set() if entry else False