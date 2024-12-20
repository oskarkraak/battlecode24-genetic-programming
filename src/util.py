import time
from typing import List

from src.mutatable import Mutatable


def code_to_string(code: List[Mutatable]) -> str:
    """Convert a list of Mutatable objects into a string representation."""
    return "\n".join(str(mutatable) for mutatable in code)

def analyze_output(output: str) -> int:
    """
    Analyze the output of the program to determine if team A won.
    Fitness is 1 if 'A' wins, otherwise 0.
    """
    # Check for match result
    if output == 0:
        raise RuntimeError("Build failed")
    if "Couldn't load player class" in output:
        raise RuntimeError("Player not loaded", output)

    if "(A) wins" in output:
        return 1
    else:
        return 0

def timestamp() -> str:
    """Return the current time as a formatted string."""
    return time.strftime("[%Y-%m-%d %H:%M:%S]")
