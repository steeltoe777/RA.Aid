"""Module for checking system dependencies required by RA.Aid."""

import subprocess
import sys
from abc import ABC, abstractmethod

# Corrected import from formatting module
from ra_aid.console.formatting import print_error


class Dependency(ABC):
    """Base class for system dependencies."""

    @abstractmethod
    def check(self):
        """Check if the dependency is installed."""
        pass


class RipGrepDependency(Dependency):
    """Dependency checker for ripgrep."""

    def check(self):
        """Check if ripgrep is installed."""
        try:
            result = subprocess.run(
                ["rg", "--version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if result.returncode != 0:
                raise FileNotFoundError()
        except (FileNotFoundError, subprocess.SubprocessError):
            print_error("Required dependency 'ripgrep' is not installed.")
            print("Please install ripgrep:")
            print("  - Ubuntu/Debian: sudo apt-get install ripgrep")
            print("  - macOS: brew install ripgrep")
            print("  - Windows: choco install ripgrep")
            print("  - Other: https://github.com/BurntSushi/ripgrep#installation")
            sys.exit(1)


def check_dependencies():
    """Check if required system dependencies are installed."""
    dependencies = [RipGrepDependency()]  # Create instances
    try:
        for dependency in dependencies:
            dependency.check()
    except Exception as e:
        print_error(f"Error checking dependencies: {e}")
        sys.exit(1)
