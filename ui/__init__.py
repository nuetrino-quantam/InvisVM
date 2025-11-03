"""
InvisVM UI Components - Modular Tab Structure
"""

from .launcher_tab import LauncherTab
from .search_tab import AppSearchLauncher
from .policies_tab import PoliciesTab
from .sandboxes_tab import SandboxesTab
from .about_tab import AboutTab
from .theme import COLORS, FONTS

__all__ = [
    'LauncherTab',
    'AppSearchLauncher',
    'PoliciesTab',
    'SandboxesTab',
    'AboutTab',
    'COLORS',
    'FONTS',
]
