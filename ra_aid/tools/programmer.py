import os
import sys
from pathlib import Path
from typing import Dict, List, Union

from langchain_core.tools import tool
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from ra_aid.logging_config import get_logger
from ra_aid.models_params import DEFAULT_BASE_LATENCY, models_params
from ra_aid.proc.interactive import run_interactive_command
from ra_aid.text.processing import truncate_output
from ra_aid.tools.memory import log_work_event
from ra_aid.database.repositories.config_repository import get_config_repository
from ra_aid.database.repositories.related_files_repository import get_related_files_repository

console = Console()
logger = get_logger(__name__)

def _truncate_for_log(text: str, max_length: int = 300) -> str:
    """Truncate text for logging, adding [truncated] if necessary."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "... [truncated]"


@tool
def run_programming_task(
    instructions: str, files: List[str] = []
) -> Dict[str, Union[str, int, bool]]:
    """Assign a programming task to a human programmer. Use this instead of trying to write code to files yourself.

    The programmer sees *ONLY* what you provide, no conversation history.

    Give detailed instructions including multi-file tasks but do not write the code in the instructions.

    Keep your instructions information dense and no more than 300 words.

    The programmer cannot run commands or see context other than related files and what you say in the instructions.

    They can add/modify files, but not remove. Use run_shell_command to remove files. If referencing files you'll delete, remove them after they finish.

    If the programmer wrote files, they actually wrote to disk. You do not need to rewrite the output of what the programmer showed you.

    Args:
     instructions: REQUIRED Programming task instructions (markdown format, use newlines and as many tokens as needed, no commands allowed)
     files: Optional; if not provided, uses related_files
    """
    # Build command
    command = [
        "aider",
        "--yes-always",
        "--no-git",
        "--no-auto-commits",
        "--dark-mode",
        "--no-suggest-shell-commands",
        "--no-show-release-notes",
        "--no-check-update",
    ]

    # Get combined list of files (explicit + related) with normalized paths
    # and deduplicated using set operations
    related_files_paths = []
    try:
        repo = get_related_files_repository()
        related_files_paths = list(repo.get_all().values())
        logger.debug("Retrieved related files from repository")
    except RuntimeError as e:
        # Repository not initialized
        logger.warning(f"Failed to get related files repository: {e}")

    files_to_use = list(
        {os.path.abspath(f) for f in (files or [])}
        | {os.path.abspath(f) for f in related_files_paths}
    )

    # Add config file if specified
    if aider_config := get_config_repository().get("aider_config"):
        command.extend(["--config", aider_config])

    # if environment variable AIDER_FLAGS exists then parse
    if "AIDER_FLAGS" in os.environ:
        # wrap in try catch in case of any error and log the error
        try:
            command.extend(parse_aider_flags(os.environ["AIDER_FLAGS"]))
        except Exception as e:
            print(f"Error parsing AIDER_FLAGS: {e}")

    # ensure message aider argument is always present
    command.append("-m")

    command.append(instructions)
    if files_to_use:
        command.extend(files_to_use)

    # Create a pretty display of what we're doing
    task_display = ["## Instructions\n", f"{instructions}\n"]

    if files_to_use:
        task_display.extend(
            ["\n## Files\n", *[f"- `{file}`\n" for file in files_to_use]]
        )

    markdown_content = "".join(task_display)
    console.print(
        Panel(
            Markdown(markdown_content),
            title="🤖 Aider Task",
            border_style="bright_blue",
        )
    )
    logger.debug(f"command: {command}")

    try:
        # Run the command interactively
        print()
        # Get provider/model specific latency coefficient
        provider = get_config_repository().get("provider", "")
        model = get_config_repository().get("model", "")
        latency = (
            models_params.get(provider, {})
            .get(model, {})
            .get("latency_coefficient", DEFAULT_BASE_LATENCY)
        )

        result = run_interactive_command(command, expected_runtime_seconds=latency)
        print()

        # Log the programming task
        log_work_event(f"Executed programming task: {_truncate_for_log(instructions)}")

        extra_ins = ""

        # Return structured output
        return {
            "output": (truncate_output(result[0].decode()) + extra_ins)
            if result[0]
            else "",
            "return_code": result[1],
            "success": result[1] == 0,
        }

    except Exception as e:
        print()
        error_text = Text()
        error_text.append("Error running programming task:\n", style="bold red")
        error_text.append(str(e), style="red")
        console.print(error_text)

        return {"output": str(e), "return_code": 1, "success": False}


def parse_aider_flags(aider_flags: str) -> List[str]:
    """Parse a string of aider flags into a list of flags and their values.

    Args:
        aider_flags: A string containing comma-separated flags, with or without leading dashes.
                    Can contain spaces around flags and commas.
                    Supports flags with values (e.g. --analytics-log filename.json)

    Returns:
        A list of flags with proper '--' prefix and their values as separate elements.

    Examples:
        >>> parse_aider_flags("yes-always,dark-mode")
        ['--yes-always', '--dark-mode']
        >>> parse_aider_flags("--yes-always, --dark-mode")
        ['--yes-always', '--dark-mode']
        >>> parse_aider_flags("--analytics-log filename.json")
        ['--analytics-log', 'filename.json']
        >>> parse_aider_flags("")
        []
    """
    if not aider_flags.strip():
        return []

    # Split by comma and strip whitespace
    flag_groups = [group.strip() for group in aider_flags.split(",")]

    result = []
    for group in flag_groups:
        if not group:
            continue

        # Split by space to separate flag from value
        parts = group.split()

        # Add '--' prefix to the flag if not present, stripping any extra dashes
        flag = parts[0].lstrip("-")  # Remove all leading dashes
        flag = f"--{flag}"  # Add exactly two dashes

        result.append(flag)

        # Add any remaining parts as separate values
        if len(parts) > 1:
            result.extend(parts[1:])

    return result


# Export the functions
__all__ = ["run_programming_task"]
