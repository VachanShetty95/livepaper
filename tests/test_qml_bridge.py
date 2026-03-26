"""Tests for the QML bridge helpers."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import QApplication

from livepaper.models import BlurMode, MonitorMode, PauseMode
from livepaper.services.wallpaper_service import WallpaperService
from livepaper.ui.qml_bridge import AppBridge


def test_open_add_dialog_accepts_dialog_string_paths(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])

    config_file = tmp_path / "config.json"
    first = tmp_path / "first.mp4"
    second = tmp_path / "second.mp4"
    first.write_bytes(b"\x00")
    second.write_bytes(b"\x00")

    monkeypatch.setattr(
        "livepaper.ui.qml_bridge.QFileDialog.getOpenFileNames",
        lambda *args, **kwargs: ([str(first), str(second)], ""),
    )
    monkeypatch.setattr(
        "livepaper.services.thumbnail_generator.generate_thumbnail",
        lambda *args, **kwargs: None,
    )

    bridge = AppBridge(WallpaperService(config_file))
    bridge.openAddDialog()
    app.processEvents()

    wallpapers = bridge.getWallpapers()
    assert len(wallpapers) == 2
    assert {item["path"] for item in wallpapers} == {str(first.resolve()), str(second.resolve())}


def test_save_config_merges_nested_settings(tmp_path: Path) -> None:
    config_file = tmp_path / "config.json"
    service = WallpaperService(config_file)
    bridge = AppBridge(service)

    bridge.saveConfig({
        "video": {
            "pause_mode": PauseMode.ACTIVE_WINDOW,
            "blur_mode": BlurMode.ALWAYS,
            "blur_radius": 55,
        },
        "playback": {
            "mute_audio": True,
            "playback_rate": 1.5,
        },
        "sync_lock_screen": True,
        "monitor_mode": MonitorMode.PER_SCREEN,
    })

    reloaded = WallpaperService(config_file).config

    assert reloaded.video.pause_mode == PauseMode.ACTIVE_WINDOW
    assert reloaded.video.blur_mode == BlurMode.ALWAYS
    assert reloaded.video.blur_radius == 55
    assert reloaded.video.battery_threshold == 20
    assert reloaded.playback.mute_audio is True
    assert reloaded.playback.playback_rate == 1.5
    assert reloaded.playback.volume == 100
    assert reloaded.sync_lock_screen is True
    assert reloaded.monitor_mode == MonitorMode.PER_SCREEN
