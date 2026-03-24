"""Python to QML Bridge for Livepaper."""

from __future__ import annotations

import os
from pathlib import Path

from PyQt6.QtCore import QObject, QThread, pyqtProperty, pyqtSignal, pyqtSlot

from livepaper.models import SystemStatus
from livepaper.services.config_manager import (
    add_wallpapers_to_library,
    remove_wallpaper_from_library,
)
from livepaper.services.system_detector import detect_system_status
from livepaper.services.wallpaper_service import WallpaperService, WallpaperTarget
from livepaper.ui.dialogs.add_wallpaper_dialog import open_add_wallpaper_dialog
from livepaper.ui.utils import open_url


class _DetectionWorker(QThread):
    finished = pyqtSignal(SystemStatus)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

    def run(self) -> None:
        status = detect_system_status()
        self.finished.emit(status)


class AppBridge(QObject):
    """Bridge converting Python backend calls to QML interface."""

    wallpapersChanged = pyqtSignal()  # noqa: N815
    configChanged = pyqtSignal()  # noqa: N815
    errorOccurred = pyqtSignal(str, str)  # noqa: N815
    systemCheckCompleted = pyqtSignal("QVariantList")  # noqa: N815

    def __init__(self, service: WallpaperService, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._service = service
        self._check_worker: _DetectionWorker | None = None

    @pyqtSlot()
    def openAddDialog(self) -> None:
        """Open the add wallpaper file picker."""
        # QFileDialog works without a parent widget, passing None.
        paths = open_add_wallpaper_dialog(None)
        if paths:
            print(f"Adding wallpapers: {paths}")
            add_wallpapers_to_library(paths)
            self._service.reload_config()
            self.wallpapersChanged.emit()

            # Start background thumbnail generation
            import threading

            from PyQt6.QtCore import QTimer

            from livepaper.services.thumbnail_generator import generate_thumbnail

            def worker():
                updated = False
                for w in self._service.config.wallpapers:
                    if not (w.thumbnail_path and w.thumbnail_path.exists()):
                        print(f"Generating thumbnail for {w.path}...")
                        try:
                            thumb = generate_thumbnail(w.path)
                            if thumb:
                                w.thumbnail_path = thumb
                                updated = True
                        except Exception as e:
                            print(f"Thumbnail failed for {w.path}: {e}")

                if updated:
                    self._service.save_config(self._service.config)

                # Reload config and signal correctly from the main thread
                def _update():
                    self._service.reload_config()
                    self.wallpapersChanged.emit()
                QTimer.singleShot(0, _update)

            threading.Thread(target=worker, daemon=True).start()

    @pyqtSlot(str)
    def removeWallpaper(self, path_str: str) -> None:
        """Remove wallpaper from library."""
        try:
            print(f"Received request to remove: {path_str}")
            remove_wallpaper_from_library(Path(path_str))
            self._service.reload_config()
            self.wallpapersChanged.emit()
            print("Successfully removed.")
        except Exception as e:
            print(f"Failed to remove wallpaper: {e}")
            self.errorOccurred.emit("Failed to remove wallpaper", str(e))

    @pyqtSlot(result="QVariantList")
    def getWallpapers(self) -> list[dict[str, str]]:
        """Return list of wallpapers for QML ListModel."""
        config = self._service.config
        res = []
        for w in config.wallpapers:
            # Format image source string for QML Image component
            # If thumbnail exists, format it as file URL, else empty
            thumb_url = f"file://{w.thumbnail_path}" if w.thumbnail_path and w.thumbnail_path.exists() else ""
            res.append({
                "name": w.name,
                "path": str(w.path),
                "imageSource": thumb_url
            })
        return res

    @pyqtSlot(result="QVariantMap")
    def getConfig(self) -> dict:
        """Return current AppConfig as dictionary."""
        return self._service.config.model_dump(mode="json")

    @pyqtSlot("QVariantMap")
    def saveConfig(self, data: dict) -> None:
        """Update and save config from QML dictionary."""
        config = self._service.config
        updated = config.model_copy(update=data)
        self._service.save_config(updated)
        self.configChanged.emit()

    @pyqtSlot(str, str)
    def applyWallpaper(self, path_str: str, target_str: str) -> None:
        """Apply a wallpaper entry to the specified target."""
        try:
            print(f"Received request to apply: {path_str} to {target_str}")
            target = WallpaperTarget(target_str)
            self._service.apply_wallpaper([Path(path_str)], target)
            print("Applied successfully.")
        except Exception as e:
            print(f"Failed to apply wallpaper: {e}")
            self.errorOccurred.emit("Failed to apply wallpaper", str(e))

    @pyqtSlot(str)
    def openUrl(self, url: str) -> None:
        """Open a system URL."""
        open_url(url)

    @pyqtProperty(str)
    def username(self) -> str:
        """Return the current system username."""
        return os.environ.get("USER", os.environ.get("USERNAME", "User"))

    @pyqtSlot()
    def runSystemCheck(self) -> None:
        """Run system check in background and emit results."""
        worker = _DetectionWorker(self)
        self._check_worker = worker
        worker.finished.connect(self._on_check_finished)
        worker.start()

    def _on_check_finished(self, status: SystemStatus) -> None:
        """Process result and emit to QML."""
        items = status.to_check_items()
        res = [
            {
                "name": item.name,
                "passed": item.passed,
                "message": item.message,
                "fix_url": item.fix_url,
            }
            for item in items
        ]
        self.systemCheckCompleted.emit(res)
