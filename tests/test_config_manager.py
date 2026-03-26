"""Tests for config manager service."""

from __future__ import annotations

from pathlib import Path

from livepaper.models import (
    AppConfig,
    BlurMode,
    FillMode,
    PauseMode,
    PlaybackConfig,
    VideoConfig,
    WallpaperEntry,
)
from livepaper.services.config_manager import (
    add_wallpapers_to_library,
    apply_lock_screen_wallpaper,
    read_app_config,
    remove_wallpaper_from_library,
    write_app_config,
)
from livepaper.services.dbus_client import PLUGIN_ID


class TestAppConfigReadWrite:
    def test_write_and_read(self, tmp_config_file: Path) -> None:
        config = AppConfig()
        config = config.model_copy(update={
            "playback": PlaybackConfig(mute_audio=True, playback_rate=1.5),
        })
        write_app_config(config, tmp_config_file)
        loaded = read_app_config(tmp_config_file)
        assert loaded.playback.mute_audio is True
        assert loaded.playback.playback_rate == 1.5

    def test_read_nonexistent_returns_default(self, tmp_path: Path) -> None:
        config = read_app_config(tmp_path / "nonexistent.json")
        assert config == AppConfig()

    def test_read_invalid_json_returns_default(self, tmp_config_file: Path) -> None:
        tmp_config_file.write_text("not valid json {{{", encoding="utf-8")
        config = read_app_config(tmp_config_file)
        assert config == AppConfig()

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        deep_path = tmp_path / "a" / "b" / "c" / "config.json"
        write_app_config(AppConfig(), deep_path)
        assert deep_path.exists()

    def test_roundtrip_with_wallpapers(self, tmp_config_file: Path, sample_video: Path) -> None:
        entry = WallpaperEntry(path=sample_video, name="Test")
        config = AppConfig(wallpapers=[entry])
        write_app_config(config, tmp_config_file)
        loaded = read_app_config(tmp_config_file)
        assert len(loaded.wallpapers) == 1
        assert loaded.wallpapers[0].name == "Test"

    def test_video_config_roundtrip(self, tmp_config_file: Path) -> None:
        config = AppConfig(video=VideoConfig(
            fill_mode=FillMode.STRETCH,
            pause_mode=PauseMode.ACTIVE_WINDOW,
            blur_mode=BlurMode.ALWAYS,
            blur_radius=75,
            battery_threshold=30,
        ))
        write_app_config(config, tmp_config_file)
        loaded = read_app_config(tmp_config_file)
        assert loaded.video.fill_mode == FillMode.STRETCH
        assert loaded.video.pause_mode == PauseMode.ACTIVE_WINDOW
        assert loaded.video.blur_mode == BlurMode.ALWAYS
        assert loaded.video.blur_radius == 75
        assert loaded.video.battery_threshold == 30

    def test_playback_config_roundtrip(self, tmp_config_file: Path) -> None:
        config = AppConfig(playback=PlaybackConfig(
            volume=60,
            random_order=True,
            fade_enabled=True,
            fade_duration=2500,
            timer=30,
        ))
        write_app_config(config, tmp_config_file)
        loaded = read_app_config(tmp_config_file)
        assert loaded.playback.volume == 60
        assert loaded.playback.random_order is True
        assert loaded.playback.fade_enabled is True
        assert loaded.playback.fade_duration == 2500
        assert loaded.playback.timer == 30


class TestLockScreenWallpaper:
    def test_creates_file_with_correct_plugin_id(self, tmp_path: Path, sample_video: Path) -> None:
        config_path = tmp_path / "kscreenlockerrc"
        apply_lock_screen_wallpaper([sample_video], kscreenlocker_path=config_path)
        content = config_path.read_text(encoding="utf-8")
        # Must use full dotted plugin ID — short ID causes black screen
        assert PLUGIN_ID in content
        assert "smart-video-wallpaper-reborn" not in content.replace(PLUGIN_ID, "")

    def test_video_urls_written(self, tmp_path: Path, sample_video: Path) -> None:
        config_path = tmp_path / "kscreenlockerrc"
        apply_lock_screen_wallpaper([sample_video], kscreenlocker_path=config_path)
        content = config_path.read_text(encoding="utf-8")
        assert "VideoUrls" in content
        assert str(sample_video.resolve()) in content

    def test_settings_written_when_config_provided(self, tmp_path: Path, sample_video: Path) -> None:
        config_path = tmp_path / "kscreenlockerrc"
        config = AppConfig(
            video=VideoConfig(
                fill_mode=FillMode.PRESERVE_ASPECT_FIT,
                pause_mode=PauseMode.ACTIVE_WINDOW,
                blur_mode=BlurMode.ALWAYS,
                blur_radius=60,
                blur_on_original_proportions=False,
            ),
            playback=PlaybackConfig(
                volume=75,
                mute_audio=True,
                random_order=True,
                loop_current_video=True,
                fade_enabled=True,
                fade_duration=1500,
            ),
        )
        apply_lock_screen_wallpaper([sample_video], config=config, kscreenlocker_path=config_path)
        content = config_path.read_text(encoding="utf-8")
        assert "FillMode" in content
        assert "PauseMode" in content
        assert "BlurMode" in content
        assert "BlurRadius" in content
        assert "Volume" in content
        assert "MuteMode" in content
        assert "RandomMode" in content
        assert "CrossfadeEnabled" in content
        assert "CrossfadeDuration" in content
        assert "FillBlur" in content
        assert '"loop":true' in content

    def test_preserves_existing_sections(self, tmp_path: Path, sample_video: Path) -> None:
        config_path = tmp_path / "kscreenlockerrc"
        config_path.write_text("[SomeOtherSection]\nSomeKey=SomeValue\n", encoding="utf-8")
        apply_lock_screen_wallpaper([sample_video], kscreenlocker_path=config_path)
        content = config_path.read_text(encoding="utf-8")
        assert "SomeOtherSection" in content
        assert "SomeKey" in content
        assert PLUGIN_ID in content

    def test_multiple_videos(self, tmp_path: Path) -> None:
        config_path = tmp_path / "kscreenlockerrc"
        videos = []
        for name in ["a.mp4", "b.mp4"]:
            v = tmp_path / name
            v.write_bytes(b"\x00")
            videos.append(v)
        apply_lock_screen_wallpaper(videos, kscreenlocker_path=config_path)
        content = config_path.read_text(encoding="utf-8")
        assert content.count("file://") == 2


class TestLibraryManagement:
    def test_add_wallpapers(self, tmp_config_file: Path, sample_video: Path) -> None:
        config = add_wallpapers_to_library([sample_video], tmp_config_file)
        assert len(config.wallpapers) == 1
        assert config.wallpapers[0].path == sample_video.resolve()

    def test_add_duplicate_ignored(self, tmp_config_file: Path, sample_video: Path) -> None:
        add_wallpapers_to_library([sample_video], tmp_config_file)
        config = add_wallpapers_to_library([sample_video], tmp_config_file)
        assert len(config.wallpapers) == 1

    def test_add_string_paths(self, tmp_config_file: Path, sample_video: Path) -> None:
        config = add_wallpapers_to_library([str(sample_video)], tmp_config_file)
        assert len(config.wallpapers) == 1
        assert config.wallpapers[0].path == sample_video.resolve()

    def test_add_nonexistent_ignored(self, tmp_config_file: Path) -> None:
        config = add_wallpapers_to_library([Path("/nonexistent/video.mp4")], tmp_config_file)
        assert len(config.wallpapers) == 0

    def test_remove_wallpaper(self, tmp_config_file: Path, sample_video: Path) -> None:
        add_wallpapers_to_library([sample_video], tmp_config_file)
        config = remove_wallpaper_from_library(sample_video, tmp_config_file)
        assert len(config.wallpapers) == 0

    def test_remove_nonexistent_no_error(self, tmp_config_file: Path, sample_video: Path) -> None:
        add_wallpapers_to_library([sample_video], tmp_config_file)
        config = remove_wallpaper_from_library(Path("/other/file.mp4"), tmp_config_file)
        assert len(config.wallpapers) == 1
