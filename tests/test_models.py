"""Tests for Pydantic models."""

from __future__ import annotations

from pathlib import Path

import pytest

from livepaper.models import (
    AppConfig,
    BlurMode,
    FillMode,
    MonitorMode,
    PauseMode,
    PlaybackConfig,
    SystemStatus,
    VideoConfig,
    WallpaperEntry,
)


class TestWallpaperEntry:
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
        entry = WallpaperEntry(path=evil_path)
        assert ".." not in entry.path.parts

    def test_thumbnail_path_optional(self, sample_video: Path) -> None:
        entry = WallpaperEntry(path=sample_video)
        assert entry.thumbnail_path is None


class TestVideoConfig:
    def test_defaults(self) -> None:
        vc = VideoConfig()
        assert vc.fill_mode == FillMode.PRESERVE_ASPECT_CROP
        assert vc.pause_mode == PauseMode.MAXIMIZED_OR_FULLSCREEN
        assert vc.blur_mode == BlurMode.NEVER
        assert vc.blur_radius == 40
        assert vc.blur_animation_duration == 300
        assert vc.blur_on_original_proportions is True
        assert vc.battery_saver_enabled is True
        assert vc.battery_threshold == 20
        assert vc.check_windows_from_all_screens is False

    def test_fill_mode_values_are_ints(self) -> None:
        # Plugin expects integer values in config
        assert FillMode.STRETCH.value == 0
        assert FillMode.PRESERVE_ASPECT_FIT.value == 1
        assert FillMode.PRESERVE_ASPECT_CROP.value == 2

    def test_pause_mode_labels(self) -> None:
        assert "fullscreen" in PauseMode.MAXIMIZED_OR_FULLSCREEN.label.lower()
        assert PauseMode.NEVER.label == "Never"

    def test_blur_mode_labels(self) -> None:
        assert BlurMode.NEVER.label == "Never"
        assert BlurMode.ALWAYS.label == "Always"
        assert "paused" in BlurMode.VIDEO_PAUSED.label.lower()

    def test_battery_threshold_bounds(self) -> None:
        with pytest.raises(ValueError):
            VideoConfig(battery_threshold=3)
        with pytest.raises(ValueError):
            VideoConfig(battery_threshold=101)


class TestPlaybackConfig:
    def test_defaults(self) -> None:
        pc = PlaybackConfig()
        assert pc.mute_audio is False
        assert pc.volume == 100
        assert pc.playback_rate == 1.0
        assert pc.playback_rate_alt == 0.25
        assert pc.loop_current_video is False
        assert pc.random_order is False
        assert pc.resume_time is False
        assert pc.timer == 0
        assert pc.fade_enabled is False
        assert pc.fade_duration == 1000

    def test_speed_bounds(self) -> None:
        pc = PlaybackConfig(playback_rate=0.1)
        assert pc.playback_rate == 0.1
        with pytest.raises(ValueError):
            PlaybackConfig(playback_rate=5.0)

    def test_volume_bounds(self) -> None:
        PlaybackConfig(volume=0)
        PlaybackConfig(volume=100)
        with pytest.raises(ValueError):
            PlaybackConfig(volume=101)


class TestAppConfig:
    def test_default_values(self) -> None:
        config = AppConfig()
        assert isinstance(config.video, VideoConfig)
        assert isinstance(config.playback, PlaybackConfig)
        assert config.sync_lock_screen is False
        assert config.monitor_mode == MonitorMode.ALL
        assert config.wallpapers == []
        assert config.first_run_complete is False

    def test_json_roundtrip(self, sample_config: AppConfig) -> None:
        json_str = sample_config.model_dump_json()
        restored = AppConfig.model_validate_json(json_str)
        assert restored.video.fill_mode == sample_config.video.fill_mode
        assert len(restored.wallpapers) == len(sample_config.wallpapers)

    def test_model_copy_immutability(self) -> None:
        original = AppConfig()
        updated = original.model_copy(update={"sync_lock_screen": True})
        assert original.sync_lock_screen is False
        assert updated.sync_lock_screen is True


class TestFillModeLabels:
    def test_all_have_labels(self) -> None:
        for mode in FillMode:
            assert mode.label
            assert isinstance(mode.label, str)


class TestSystemStatus:
    def test_all_checks_passed(self) -> None:
        status = SystemStatus(
            plasma_version="6.1.0",
            plasma_ok=True,
            plugin_installed=True,
            codecs_available=True,
        )
        assert status.all_checks_passed is True

    def test_partial_failure(self) -> None:
        status = SystemStatus(plasma_ok=True, plugin_installed=False, codecs_available=True)
        assert status.all_checks_passed is False

    def test_to_check_items(self) -> None:
        status = SystemStatus(
            plasma_version="6.1.0", plasma_ok=True, plugin_installed=False, codecs_available=True
        )
        items = status.to_check_items()
        assert len(items) == 3
        assert items[0].passed is True
        assert items[1].passed is False
        assert items[1].fix_url != ""
