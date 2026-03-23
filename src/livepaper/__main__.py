"""Livepaper entry point."""

from __future__ import annotations

import os
import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtCore import QUrl

from livepaper import __app_name__, __version__
from livepaper.services.wallpaper_service import WallpaperService
from livepaper.ui.qml_bridge import AppBridge


def main() -> None:
    """Launch the Livepaper application."""
    # Use QApplication because QFileDialog uses widgets
    app = QApplication(sys.argv)
    app.setApplicationName(__app_name__)
    app.setApplicationVersion(__version__)
    app.setDesktopFileName("livepaper")

    engine = QQmlApplicationEngine()
    
    # Initialize backend services
    service = WallpaperService()
    
    # Setup QML Bridge
    bridge = AppBridge(service)
    engine.rootContext().setContextProperty("appBridge", bridge)
    
    # Path to main.qml
    current_dir = os.path.dirname(os.path.abspath(__file__))
    qml_file = os.path.join(current_dir, "ui", "qml", "main.qml")
    
    engine.load(QUrl.fromLocalFile(qml_file))

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
