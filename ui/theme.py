"""
InvisVM Theme Manager - Centralized colors and styles
"""

from PyQt5.QtGui import QFont

# Modern Color Scheme
COLORS = {
    'primary': '#2196F3',
    'primary_dark': '#1976D2',
    'accent': '#4CAF50',
    'accent_hover': '#45a049',
    'danger': '#f44336',
    'danger_dark': '#d32f2f',
    'bg_light': '#f5f5f5',
    'bg_white': '#ffffff',
    'text_primary': '#212121',
    'text_secondary': '#757575',
    'border': '#e0e0e0',
    'tab_bg': '#fafafa',
}

# Font definitions
FONTS = {
    'logo': ('Segoe UI', 18, QFont.Bold),
    'title': ('Segoe UI', 14, QFont.Bold),
    'subtitle': ('Segoe UI', 10, QFont.Normal),
}

def get_button_style(bg_color=None, text_color=None, border_color=None):
    """Generate button stylesheet"""
    bg = bg_color or COLORS['bg_light']
    text = text_color or COLORS['text_primary']
    border = border_color or COLORS['border']
    
    return f"""
        QPushButton {{
            background-color: {bg};
            color: {text};
            border: 1.5px solid {border};
            padding: 10px 14px;
            border-radius: 6px;
            font-weight: 500;
            font-size: 10pt;
        }}
        QPushButton:hover {{
            background-color: {COLORS['primary']};
            color: white;
            border: 1.5px solid {COLORS['primary']};
        }}
    """

def get_card_style():
    """Generate card stylesheet"""
    return f"""
        background-color: {COLORS['bg_white']};
        border: 1px solid {COLORS['border']};
        border-radius: 10px;
    """

def get_search_style():
    """Generate search input stylesheet"""
    return f"""
        QLineEdit {{
            padding: 12px 16px;
            font-size: 11pt;
            border: 1.5px solid {COLORS['border']};
            border-radius: 7px;
            background-color: {COLORS['bg_white']};
            color: {COLORS['text_primary']};
        }}
        QLineEdit:focus {{
            border: 1.5px solid {COLORS['primary']};
            background-color: {COLORS['bg_white']};
        }}
    """

def get_table_style():
    """Generate table stylesheet"""
    return f"""
        QTableWidget {{
            background-color: {COLORS['bg_white']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            gridline-color: {COLORS['border']};
        }}
        QTableWidget::item {{
            padding: 10px;
            border: none;
        }}
        QHeaderView::section {{
            background-color: {COLORS['bg_light']};
            padding: 10px;
            border: none;
            font-weight: 600;
            font-size: 10pt;
        }}
    """
