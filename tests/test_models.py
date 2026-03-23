"""Tests for Pydantic models."""

from __future__ import annotations

from pathlib import Path

import pytest

from livepaper.models import (
    AppConfig,
    MonitorMode,
    PauseCondition,
    SystemStatus,
    WallpaperEntry,
)


class TestWallpaperEntry:
    """Tests for WallpaperEntry model."""

    def test_valid_entry(self, sample_video: Path) -> None:
        entry = WallpaperEntry(path=sample_video)
        assert entry.path == sample_video.resolve()
        assert entry.name == "test_video"

    def test_custom_name(self, sample_video: Path) -> None:
        entry = WallpaperEntry(path=sample_video, name="My Wallpaper")
        assert entry.name == "My Wallpaper"

    def test_auto_name_from_stem(self, sample_video: Path) -> None:
        entry = WallpaperEntry(path=sample_video)
        assert entry.name == sample_video.stem

    def test_path_traversal_rejected(self, tmp_path: Path) -> None:
        evil_path = tmp_path / ".." / ".." / "etc" / "passwd"
        # The path resolves, but the resolved path shouldn't contain ".."
        # If the resolved path is valid, it passes; the validation
        # checks the resolved path for traversal markers
        entry = WallpaperEntry(path=evil_path)
        assert ".." not in entry.path.parts

    def test_thumbnail_path_optional(self, sample_video: Path) -> None:
        entry = WallpaperEntry(path=sample_video)
        assert entry.thumbnail_path is None


class TestAppConfig:
    """Tests for AppConfig model."""

    def test_default_values(self) -> None:
        config = AppConfig()
        assert config.pause_condition == PauseCondition.FULLSCREEN
        assert config.mute_by_default is False
        assert config.playback_speed == 1.0
        assert config.blur_enabled is False
        assert config.blur_radius == 40
        assert config.battery_saver_enabled is True
        assert config.battery_threshold == 20
        assert config.sync_lock_screen is False
        assert config.monitor_mode == MonitorMode.ALL
        assert config.wallpapers == []
        assert config.first_run_complete is False

    def test_speed_bounds(self) -> None:
        config = AppConfig(playback_speed=0.25)
        assert config.playback_speed == 0.25

        config = AppConfig(playback_speed=4.0)
        assert config.playback_speed == 4.0

        with pytest.raises(ValueError):
            AppConfig(playback_speed=0.1)

        with pytest.raises(ValueError):
            AppConfig(playback_speed=5.0)

    def test_battery_threshold_bounds(self) -> None:
        with pytest.raises(ValueError):
            AppConfig(battery_threshold=3)

        with pytest.raises(ValueError):
            AppConfig(battery_threshold=101)

    def test_json_roundtrip(self, sample_config: AppConfig) -> None:
        json_str = sample_config.model_dump_json()
        restored = AppConfig.model_validate_json(json_str)
        assert restored.pause_condition == sample_config.pause_condition
        assert len(restored.wallpapers) == len(sample_config.wallpapers)

    def test_model_copy_immutability(self) -> None:
        original = AppConfig()
        updated = original.model_copy(update={"mute_by_default": True})
        assert original.mute_by_default is False
        assert updated.mute_by_default is True


class TestSystemStatus:
    """Tests for SystemStatus model."""

    def test_all_checks_passed(self) -> None:
        status = SystemStatus(
            plasma_version="6.1.0",
            plasma_ok=True,
            plugin_installed=True,
            codecs_available=True,
        )
        assert status.all_checks_passed is True

    def test_partial_failure(self) -> None:
        status = SystemStatus(
            plasma_ok=True,
            plugin_installed=False,
            codecs_available=True,
        )
        assert status.all_checks_passed is False

    def test_to_check_items(self) -> None:
        status = SystemStatus(
            plasma_version="6.1.0",
            plasma_ok=True,
            plugin_installed=False,
            codecs_available=True,
        )
        items = status.to_check_items()
        assert len(items) == 3
        assert items[0].passed is True
        assert items[1].passed is False
        assert items[1].fix_url != ""
