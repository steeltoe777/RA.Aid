import threading
from typing import Dict, Any

# Global registry mapping session_id -> { thread, stop_event }
agent_thread_registry: Dict[int, Dict[str, Any]] = {}

def stop_agent(session_id: int) -> bool:
    entry = agent_thread_registry.get(session_id)
    if entry and "stop_event" in entry:
        entry["stop_event"].set()
        return True
    return False

def is_agent_running(session_id: int) -> bool:
    entry = agent_thread_registry.get(session_id)
    return entry and entry["thread"].is_alive()
