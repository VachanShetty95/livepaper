"""Pydantic models for Livepaper configuration and data."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class PauseCondition(StrEnum):
    """When to pause the video wallpaper."""

    NEVER = "never"
    FULLSCREEN = "fullscreen"
    MAXIMIZED = "maximized"
    ACTIVE_WINDOW = "active_window"


class BlurCondition(StrEnum):
    """When to apply blur effect."""

    NEVER = "never"
    ALWAYS = "always"
    FULLSCREEN = "fullscreen"
    MAXIMIZED = "maximized"
    VIDEO_PAUSED = "video_paused"


class MonitorMode(StrEnum):
    """How to apply wallpaper across monitors."""

    ALL = "all"
    PER_SCREEN = "per_screen"


class WallpaperEntry(BaseModel):
    """A single video wallpaper in the library."""

    path: Path
    name: str = ""
    thumbnail_path: Path | None = None

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: Path) -> Path:
        """Ensure the video path is absolute and uses no traversal."""
        resolved = v.resolve()
        if ".." in resolved.parts:
            msg = f"Path traversal not allowed: {v}"
            raise ValueError(msg)
        return resolved

    def model_post_init(self, __context: object) -> None:
        """Auto-derive name from filename if not provided."""
        if not self.name:
            object.__setattr__(self, "name", self.path.stem)


class AppConfig(BaseModel):
    """Application settings persisted to disk."""

    # Playback
    pause_condition: PauseCondition = PauseCondition.FULLSCREEN
    mute_by_default: bool = False
    playback_speed: float = Field(default=1.0, ge=0.25, le=4.0)

    # Blur
    blur_enabled: bool = False
    blur_radius: int = Field(default=40, ge=0, le=100)

    # Battery
    battery_saver_enabled: bool = True
    battery_threshold: int = Field(default=20, ge=5, le=100)

    # Lock screen
    sync_lock_screen: bool = False

    # Monitors
    monitor_mode: MonitorMode = MonitorMode.ALL

    # Library
    wallpapers: list[WallpaperEntry] = Field(default_factory=list)

    # First-run flag
    first_run_complete: bool = False


class SystemCheckItem(BaseModel):
    """Single item in the system health check."""

    name: str
    passed: bool
    message: str
    fix_url: str = ""


class SystemStatus(BaseModel):
    """Result of the system health check."""

    plasma_version: str = ""
    plasma_ok: bool = False
    plugin_installed: bool = False
    codecs_available: bool = False

    @property
    def all_checks_passed(self) -> bool:
        """Return True if all system checks pass."""
        return self.plasma_ok and self.plugin_installed and self.codecs_available

    def to_check_items(self) -> list[SystemCheckItem]:
        """Convert to a list of displayable check items."""
        return [
            SystemCheckItem(
                name="KDE Plasma 6",
                passed=self.plasma_ok,
                message=f"Version {self.plasma_version}" if self.plasma_ok else "Not detected",
                fix_url="https://kde.org/plasma-desktop/",
            ),
            SystemCheckItem(
                name="Smart Video Wallpaper Plugin",
                passed=self.plugin_installed,
                message="Installed" if self.plugin_installed else "Not installed",
                fix_url="https://aur.archlinux.org/packages/plasma6-wallpapers-smart-video-wallpaper-reborn",
            ),
            SystemCheckItem(
                name="Media Codecs (qt6-multimedia-ffmpeg)",
                passed=self.codecs_available,
                message="Available" if self.codecs_available else "Missing",
                fix_url="https://wiki.archlinux.org/title/Codecs_and_containers#Video_codecs",
            ),
        ]
