"""Tests for config manager service."""

from __future__ import annotations

from pathlib import Path

from livepaper.models import AppConfig, WallpaperEntry
from livepaper.services.config_manager import (
    add_wallpapers_to_library,
    apply_lock_screen_wallpaper,
    read_app_config,
    remove_wallpaper_from_library,
    write_app_config,
)


class TestAppConfigReadWrite:
    """Tests for config file read/write."""

    def test_write_and_read(self, tmp_config_file: Path) -> None:
        config = AppConfig(mute_by_default=True, playback_speed=1.5)
        write_app_config(config, tmp_config_file)

        loaded = read_app_config(tmp_config_file)
        assert loaded.mute_by_default is True
        assert loaded.playback_speed == 1.5

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

    def test_roundtrip_with_wallpapers(
        self, tmp_config_file: Path, sample_video: Path
    ) -> None:
        entry = WallpaperEntry(path=sample_video, name="Test")
        config = AppConfig(wallpapers=[entry])
        write_app_config(config, tmp_config_file)

        loaded = read_app_config(tmp_config_file)
        assert len(loaded.wallpapers) == 1
        assert loaded.wallpapers[0].name == "Test"


class TestLockScreenWallpaper:
    """Tests for kscreenlockerrc editing."""

    def test_creates_file(self, tmp_path: Path, sample_video: Path) -> None:
        config_path = tmp_path / "kscreenlockerrc"
        apply_lock_screen_wallpaper([sample_video], config_path)

        assert config_path.exists()
        content = config_path.read_text(encoding="utf-8")
        assert "smart-video-wallpaper-reborn" in content
        assert "VideoUrls" in content
        assert str(sample_video.resolve()) in content

    def test_preserves_existing_content(
        self, tmp_path: Path, sample_video: Path
    ) -> None:
        config_path = tmp_path / "kscreenlockerrc"
        config_path.write_text(
            "[SomeOtherSection]\nSomeKey=SomeValue\n",
            encoding="utf-8",
        )

        apply_lock_screen_wallpaper([sample_video], config_path)

        content = config_path.read_text(encoding="utf-8")
        assert "SomeOtherSection" in content
        assert "SomeKey" in content
        assert "smart-video-wallpaper-reborn" in content

    def test_multiple_videos(self, tmp_path: Path) -> None:
        config_path = tmp_path / "kscreenlockerrc"
        videos = []
        for name in ["a.mp4", "b.mp4"]:
            v = tmp_path / name
            v.write_bytes(b"\x00")
            videos.append(v)

        apply_lock_screen_wallpaper(videos, config_path)
        content = config_path.read_text(encoding="utf-8")
        assert content.count("file://") == 2


class TestLibraryManagement:
    """Tests for adding/removing wallpapers from library."""

    def test_add_wallpapers(
        self, tmp_config_file: Path, sample_video: Path
    ) -> None:
        config = add_wallpapers_to_library([sample_video], tmp_config_file)
        assert len(config.wallpapers) == 1
        assert config.wallpapers[0].path == sample_video.resolve()

    def test_add_duplicate_ignored(
        self, tmp_config_file: Path, sample_video: Path
    ) -> None:
        add_wallpapers_to_library([sample_video], tmp_config_file)
        config = add_wallpapers_to_library([sample_video], tmp_config_file)
        assert len(config.wallpapers) == 1

    def test_add_nonexistent_ignored(self, tmp_config_file: Path) -> None:
        config = add_wallpapers_to_library(
            [Path("/nonexistent/video.mp4")], tmp_config_file
        )
        assert len(config.wallpapers) == 0

    def test_remove_wallpaper(
        self, tmp_config_file: Path, sample_video: Path
    ) -> None:
        add_wallpapers_to_library([sample_video], tmp_config_file)
        config = remove_wallpaper_from_library(sample_video, tmp_config_file)
        assert len(config.wallpapers) == 0

    def test_remove_nonexistent_no_error(
        self, tmp_config_file: Path, sample_video: Path
    ) -> None:
        add_wallpapers_to_library([sample_video], tmp_config_file)
        config = remove_wallpaper_from_library(
            Path("/other/file.mp4"), tmp_config_file
        )
        assert len(config.wallpapers) == 1
