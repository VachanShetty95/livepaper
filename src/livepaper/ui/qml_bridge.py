"""Python to QML Bridge for Livepaper."""

from __future__ import annotations

import os
import typing
from pathlib import Path

from PyQt6.QtCore import (
    QAbstractListModel,
    QByteArray,
    QModelIndex,
    QObject,
    Qt,
    QThread,
    pyqtProperty,
    pyqtSignal,
    pyqtSlot,
)

from livepaper.models import AppConfig, BlurMode, FillMode, SystemStatus
from livepaper.services.config_manager import (
    add_wallpapers_to_library,
    remove_wallpaper_from_library,
)
from livepaper.services.system_detector import detect_system_status
from livepaper.services.wallpaper_service import WallpaperService, WallpaperTarget
from PyQt6.QtWidgets import QFileDialog
from livepaper.ui.utils import open_url


class _DetectionWorker(QThread):
    finished = pyqtSignal(SystemStatus)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

    def run(self) -> None:
        status = detect_system_status()
        self.finished.emit(status)


def _deep_merge(base: dict[str, typing.Any], updates: dict[str, typing.Any]) -> dict[str, typing.Any]:
    """Recursively merge dictionaries while preserving existing nested values."""
    merged = dict(base)
    for key, value in updates.items():
        existing = merged.get(key)
        if isinstance(existing, dict) and isinstance(value, dict):
            merged[key] = _deep_merge(existing, value)
        else:
            merged[key] = value
    return merged


class WallpaperListModel(QAbstractListModel):
    NameRole = Qt.ItemDataRole.UserRole + 1
    PathRole = Qt.ItemDataRole.UserRole + 2
    ImageSourceRole = Qt.ItemDataRole.UserRole + 3

    def __init__(self, service: WallpaperService, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._service = service

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: B008
        return len(self._service.config.wallpapers)

    def data(self, index: QModelIndex, role: int) -> typing.Any:
        if not index.isValid():
            return None
        w = self._service.config.wallpapers[index.row()]
        if role == self.NameRole:
            return w.name
        elif role == self.PathRole:
            return str(w.path)
        elif role == self.ImageSourceRole:
            return f"file://{w.thumbnail_path}" if w.thumbnail_path and w.thumbnail_path.exists() else ""
        return None

    def roleNames(self) -> dict[int, QByteArray]:
        return {
            self.NameRole: b"name",
            self.PathRole: b"path",
            self.ImageSourceRole: b"imageSource",
        }

    def reload(self) -> None:
        self.beginResetModel()
        self._service.reload_config()
        self.endResetModel()


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
        self._wallpaper_model = WallpaperListModel(service, self)

    @pyqtProperty(QObject, constant=True)
    def wallpaperModel(self) -> WallpaperListModel:
        return self._wallpaper_model

    @pyqtProperty(int, notify=configChanged)
    def fillMode(self) -> int:
        return self._service.config.video.fill_mode

    @fillMode.setter
    def fillMode(self, value: int) -> None:
        self._service.config.video.fill_mode = FillMode(value)
        self._service.save_config(self._service.config)
        self.configChanged.emit()

    @pyqtProperty(int, notify=configChanged)
    def blurMode(self) -> int:
        return self._service.config.video.blur_mode

    @blurMode.setter
    def blurMode(self, value: int) -> None:
        self._service.config.video.blur_mode = BlurMode(value)
        self._service.save_config(self._service.config)
        self.configChanged.emit()

    @pyqtProperty(bool, notify=configChanged)
    def fillBlur(self) -> bool:  # noqa: N802
        return self._service.config.video.blur_on_original_proportions

    @fillBlur.setter
    def fillBlur(self, value: bool) -> None:  # noqa: N802
        self._service.config.video.blur_on_original_proportions = value
        self._service.save_config(self._service.config)
        self.configChanged.emit()

    @pyqtProperty(bool, notify=configChanged)
    def loop(self) -> bool:
        return self._service.config.playback.loop_current_video

    @loop.setter
    def loop(self, value: bool) -> None:
        self._service.config.playback.loop_current_video = value
        self._service.save_config(self._service.config)
        self.configChanged.emit()

    @pyqtProperty(bool, notify=configChanged)
    def muteAudio(self) -> bool:
        return self._service.config.playback.mute_audio

    @muteAudio.setter
    def muteAudio(self, value: bool) -> None:
        self._service.config.playback.mute_audio = value
        self._service.save_config(self._service.config)
        self.configChanged.emit()

    @pyqtProperty(float, notify=configChanged)
    def playbackRate(self) -> float:
        return self._service.config.playback.playback_rate

    @playbackRate.setter
    def playbackRate(self, value: float) -> None:
        self._service.config.playback.playback_rate = max(0.1, min(value, 4.0))
        self._service.save_config(self._service.config)
        self.configChanged.emit()

    @pyqtSlot()
    def openAddDialog(self) -> None:
        """Open the add wallpaper file picker."""
        paths, _ = QFileDialog.getOpenFileNames(
            None,
            "Select Wallpapers",
            "",
            "Video Files (*.mp4 *.webm *.mkv);;All Files (*)",
        )
        if paths:
            print(f"Adding wallpapers: {paths}")
            path_items = [Path(path) for path in paths]
            add_wallpapers_to_library(path_items, self._service.config_file)
            self._wallpaper_model.reload()
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
                    self._wallpaper_model.reload()
                    self.wallpapersChanged.emit()
                QTimer.singleShot(0, _update)

            threading.Thread(target=worker, daemon=True).start()

    @pyqtSlot(str)
    def removeWallpaper(self, path_str: str) -> None:
        """Remove wallpaper from library."""
        try:
            print(f"Received request to remove: {path_str}")
            remove_wallpaper_from_library(Path(path_str), self._service.config_file)
            self._wallpaper_model.reload()
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
        try:
            merged = _deep_merge(self._service.config.model_dump(mode="json"), data)
            updated = AppConfig.model_validate(merged)
        except Exception as e:
            self.errorOccurred.emit("Failed to save settings", str(e))
            return

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
