"""Test configuration.

Ensures the project root is importable when pytest is launched from VS Code,
Windows PowerShell, or a parent directory.
"""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
root_str = str(PROJECT_ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)
