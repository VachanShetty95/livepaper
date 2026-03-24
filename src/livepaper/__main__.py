"""Livepaper entry point."""

from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtWidgets import QApplication

from livepaper import __app_name__, __version__
from livepaper.services.wallpaper_service import WallpaperService
from livepaper.ui.qml_bridge import AppBridge


def main() -> None:
    """Launch the Livepaper application."""
    app = QApplication(sys.argv)
    app.setApplicationName(__app_name__)
    app.setApplicationVersion(__version__)
    app.setDesktopFileName("livepaper")

    service = WallpaperService()
    bridge = AppBridge(service)

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("appBridge", bridge)

    qml_file = Path(__file__).parent / "ui" / "qml" / "main.qml"
    engine.load(str(qml_file))

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
