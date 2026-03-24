"""High-level wallpaper orchestration service."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from livepaper.models import AppConfig
from livepaper.services.config_manager import (
    apply_lock_screen_wallpaper,
    read_app_config,
    write_app_config,
)
from livepaper.services.dbus_client import apply_desktop_wallpaper


class WallpaperTarget(StrEnum):
    DESKTOP = "desktop"
    LOCK_SCREEN = "lock screen"
    BOTH = "both"


class WallpaperService:
    """Facade coordinating DBus and config-file operations."""

    def __init__(self, config_file: Path | None = None) -> None:
        self._config_file = config_file
        self._config = read_app_config(config_file)

    @property
    def config(self) -> AppConfig:
        return self._config

    def reload_config(self) -> AppConfig:
        self._config = read_app_config(self._config_file)
        return self._config

    def save_config(self, config: AppConfig) -> None:
        self._config = config
        write_app_config(config, self._config_file)

    def apply_wallpaper(
        self,
        video_paths: list[Path],
        target: WallpaperTarget = WallpaperTarget.DESKTOP,
        screen_index: int = -1,
    ) -> None:
        """Apply video wallpaper(s) to the specified target.

        Passes the full AppConfig to both the desktop DBus call and the
        lock screen config write, so all settings (fill mode, pause mode,
        blur, battery, playback speed, volume, etc.) are applied consistently.
        """
        cfg = self._config

        if target in (WallpaperTarget.DESKTOP, WallpaperTarget.BOTH):
            apply_desktop_wallpaper(
                video_paths,
                screen_index=screen_index,
                video_config=cfg.video,
                playback_config=cfg.playback,
            )

        if target in (WallpaperTarget.LOCK_SCREEN, WallpaperTarget.BOTH):
            apply_lock_screen_wallpaper(video_paths, config=cfg)
