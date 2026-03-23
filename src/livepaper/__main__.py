"""Livepaper entry point."""

from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from livepaper import __app_name__, __version__
from livepaper.ui.main_window import MainWindow


def main() -> None:
    """Launch the Livepaper application."""
    app = QApplication(sys.argv)
    app.setApplicationName(__app_name__)
    app.setApplicationVersion(__version__)
    app.setDesktopFileName("livepaper")

    # Use system style (Breeze on KDE) — no hardcoded theme
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
