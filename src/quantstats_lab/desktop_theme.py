"""Accessible, compact visual system shared across native Windows, macOS and Linux.

The global palette is deliberate: Qt's popup lists and native controls otherwise
retain platform light-theme colours while the surrounding window is dark.
"""

from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication, QWidget


def colours(dark: bool) -> dict[str, str]:
    if dark:
        return {
            "bg": "#0B1220",
            "side": "#0D1829",
            "panel": "#101E30",
            "input": "#15283C",
            "chart": "#0C192B",
            "text": "#E8EFF5",
            "muted": "#A6B9C7",
            "border": "#284057",
            "hover": "#1C344A",
            "accent": "#40CDC2",
            "active": "#15504F",
            "accent_text": "#051E22",
            "disabled": "#72889A",
            "grid": "#334E60",
        }
    return {
        "bg": "#F5F7FA",
        "side": "#FFFFFF",
        "panel": "#FFFFFF",
        "input": "#FFFFFF",
        "chart": "#FFFFFF",
        "text": "#1B2938",
        "muted": "#556A79",
        "border": "#CAD7E1",
        "hover": "#EDF3F7",
        "accent": "#007F7B",
        "active": "#D5F2EE",
        "accent_text": "#FFFFFF",
        "disabled": "#8294A1",
        "grid": "#D8E0E7",
    }


def stylesheet(dark: bool) -> str:
    c = colours(dark)
    mono = "'Menlo', 'Consolas', 'DejaVu Sans Mono', monospace"
    return f"""
        QWidget {{
            color: {c['text']};
            font-size: 12px;
        }}
        QMainWindow, QWidget#centralRoot, QStackedWidget#workPages {{
            background: {c['bg']};
        }}
        QFrame#sidebar {{
            background: {c['side']};
            border-right: 1px solid {c['border']};
        }}
        QFrame#sidebar QLabel {{
            color: {c['muted']};
            background: transparent;
        }}
        QLabel#brandName {{
            color: {c['text']};
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 0.7px;
        }}
        QLabel#brandTagline {{
            color: {c['muted']};
            font-size: 9px;
        }}
        QLabel#sidebarCaption, QLabel#eyebrow {{
            color: {c['muted']};
            font-size: 10px;
            font-weight: 600;
        }}
        QLabel#pageTitle {{
            color: {c['text']};
            font-size: 21px;
            font-weight: 700;
        }}
        QLabel#subtitle {{
            color: {c['muted']};
            font-size: 11px;
        }}
        QListWidget#navigation {{
            background: transparent;
            border: none;
            outline: 0;
            font-size: 12px;
        }}
        QListWidget#navigation::item {{
            color: {c['muted']};
            min-height: 23px;
            padding: 8px 11px;
            margin: 1px 0;
            border-radius: 6px;
        }}
        QListWidget#navigation::item:hover {{
            background: {c['hover']};
            color: {c['text']};
        }}
        QListWidget#navigation::item:selected {{
            background: {c['active']};
            color: {c['text'] if dark else '#0A5552'};
            font-weight: 600;
        }}
        QFrame#controlPanel {{
            background: {c['panel']};
            border: 1px solid {c['border']};
            border-radius: 8px;
        }}
        QGroupBox {{
            border: none;
            background: transparent;
            color: {c['muted']};
            font-size: 11px;
            font-weight: 600;
            padding-top: 5px;
            margin-top: 7px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 0px;
        }}
        QStackedWidget#parameterStack, QWidget#parameterPanel {{
            background: transparent;
            border: none;
        }}
        QLabel#fieldLabel {{
            color: {c['muted']};
            font-size: 11px;
        }}
        QComboBox, QLineEdit, QPlainTextEdit {{
            background: {c['input']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 5px;
            padding: 4px 8px;
            selection-background-color: {c['accent']};
            selection-color: {c['accent_text']};
            font-size: 12px;
        }}
        QComboBox:hover, QLineEdit:hover, QPlainTextEdit:hover {{
            border-color: {c['muted']};
        }}
        QComboBox:focus, QLineEdit:focus, QPlainTextEdit:focus {{
            border: 1px solid {c['accent']};
        }}
        QLineEdit {{
            font-family: 'Menlo', 'Consolas', 'DejaVu Sans Mono', monospace;
        }}
        QComboBox {{
            padding-right: 28px;
        }}
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 24px;
            border-left: 1px solid {c['border']};
            background: transparent;
        }}
        QComboBox QAbstractItemView {{
            background: {c['panel']};
            color: {c['text']};
            border: 1px solid {c['border']};
            outline: 0;
            selection-background-color: {c['active']};
            selection-color: {c['text'] if dark else '#0A5552'};
            padding: 3px;
        }}
        QPlainTextEdit#summary {{
            background: {c['panel']};
            border: none;
            border-top: 1px solid {c['border']};
            border-radius: 0;
            font-family: {mono};
            font-size: 11px;
            selection-background-color: {c['accent']};
        }}
        QWidget#plotPanel {{
            background: {c['chart']};
            border: 1px solid {c['border']};
            border-radius: 8px;
        }}
        QPushButton, QToolButton {{
            background: {c['input']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 5px;
            min-height: 24px;
            padding: 4px 10px;
            font-size: 11px;
        }}
        QPushButton:hover, QToolButton:hover {{
            background: {c['hover']};
            border-color: {c['accent']};
        }}
        QPushButton#primaryButton {{
            background: {c['accent']};
            color: {c['accent_text']};
            border: 1px solid {c['accent']};
            font-weight: 700;
        }}
        QPushButton#primaryButton:hover {{
            background: {c['accent']};
        }}
        QToolButton#plotTool {{
            background: transparent;
            color: {c['muted']};
            border: none;
            min-height: 20px;
            padding: 2px 8px;
            font-size: 11px;
        }}
        QToolButton#plotTool:hover {{
            background: {c['hover']};
            color: {c['text']};
        }}
        QPushButton:disabled, QToolButton:disabled {{
            color: {c['disabled']};
            border-color: {c['border']};
            background: {c['panel']};
        }}
        QSplitter::handle {{
            background: transparent;
            border: none;
        }}
        QScrollBar:vertical {{
            background: transparent;
            width: 7px;
            border: none;
        }}
        QScrollBar::handle:vertical {{
            background: {c['border']};
            border-radius: 3px;
            min-height: 25px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}
    """


def apply_palette(window: QWidget, dark: bool) -> None:
    """Set both Qt's actual widget palette and CSS to avoid unreadable combo menus."""
    c = colours(dark)
    app = QApplication.instance()
    palette = QPalette()
    for role, key in (
        (QPalette.ColorRole.Window, "bg"),
        (QPalette.ColorRole.Base, "input"),
        (QPalette.ColorRole.AlternateBase, "panel"),
        (QPalette.ColorRole.Button, "input"),
        (QPalette.ColorRole.Text, "text"),
        (QPalette.ColorRole.WindowText, "text"),
        (QPalette.ColorRole.ButtonText, "text"),
        (QPalette.ColorRole.Highlight, "accent"),
        (QPalette.ColorRole.HighlightedText, "accent_text"),
        (QPalette.ColorRole.ToolTipBase, "panel"),
        (QPalette.ColorRole.ToolTipText, "text"),
    ):
        palette.setColor(role, QColor(c[key]))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(c["disabled"]))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(c["disabled"]))
    if app is not None:
        app.setPalette(palette)
    window.setPalette(palette)
    window.setStyleSheet(stylesheet(dark))
