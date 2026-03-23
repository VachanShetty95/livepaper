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
    """Where to apply the wallpaper."""

    DESKTOP = "desktop"
    LOCK_SCREEN = "lock_screen"
    BOTH = "both"


class WallpaperService:
    """Facade coordinating DBus and config operations."""

    def __init__(self, config_file: Path | None = None) -> None:
        self._config_file = config_file
        self._config = read_app_config(config_file)

    @property
    def config(self) -> AppConfig:
        """Return current application config."""
        return self._config

    def reload_config(self) -> AppConfig:
        """Reload config from disk."""
        self._config = read_app_config(self._config_file)
        return self._config

    def save_config(self, config: AppConfig) -> None:
        """Save updated config to disk."""
        self._config = config
        write_app_config(config, self._config_file)

    def apply_wallpaper(
        self,
        video_paths: list[Path],
        target: WallpaperTarget = WallpaperTarget.DESKTOP,
        screen_index: int = -1,
    ) -> None:
        """Apply video wallpaper(s) to the specified target.

        Args:
            video_paths: List of video file paths.
            target: Where to apply (desktop, lock screen, or both).
            screen_index: Screen index for desktop (-1 = all screens).

        Raises:
            FileNotFoundError: If any video file doesn't exist.
            dbus_client.DBusError: If the DBus command fails.
        """
        if target in (WallpaperTarget.DESKTOP, WallpaperTarget.BOTH):
            apply_desktop_wallpaper(video_paths, screen_index)

        if target in (WallpaperTarget.LOCK_SCREEN, WallpaperTarget.BOTH):
            apply_lock_screen_wallpaper(video_paths)
