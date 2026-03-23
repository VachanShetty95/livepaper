"""Tests for DBus client service."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from livepaper.services.dbus_client import (
    DBusError,
    _build_wallpaper_script,
    _sanitize_path,
    apply_desktop_wallpaper,
    get_evaluate_script_command,
)


class TestSanitizePath:
    """Tests for path sanitization."""

    def test_normal_path(self, sample_video: Path) -> None:
        result = _sanitize_path(sample_video)
        assert "'" not in result or "\\'" in result
        assert str(sample_video.resolve()) in result or result == str(sample_video.resolve())

    def test_path_with_spaces(self, tmp_path: Path) -> None:
        video = tmp_path / "my video file.mp4"
        video.write_bytes(b"\x00")
        result = _sanitize_path(video)
        assert "my video file" in result

    def test_path_with_quotes(self, tmp_path: Path) -> None:
        video = tmp_path / "it's a video.mp4"
        video.write_bytes(b"\x00")
        result = _sanitize_path(video)
        assert "\\'" in result


class TestBuildWallpaperScript:
    """Tests for JS script generation."""

    def test_single_video(self, sample_video: Path) -> None:
        script = _build_wallpaper_script([sample_video])
        assert "smart-video-wallpaper-reborn" in script
        assert "VideoUrls" in script
        assert "file://" in script

    def test_multiple_videos(self, tmp_path: Path) -> None:
        videos = []
        for name in ["a.mp4", "b.mp4", "c.mp4"]:
            v = tmp_path / name
            v.write_bytes(b"\x00")
            videos.append(v)

        script = _build_wallpaper_script(videos)
        assert script.count("file://") == 3

    def test_specific_screen(self, sample_video: Path) -> None:
        script = _build_wallpaper_script([sample_video], screen_index=1)
        assert "d.screen === 1" in script

    def test_all_screens(self, sample_video: Path) -> None:
        script = _build_wallpaper_script([sample_video], screen_index=-1)
        assert "-1 < 0" in script


class TestApplyDesktopWallpaper:
    """Tests for applying wallpaper via DBus."""

    def test_file_not_found(self) -> None:
        with pytest.raises(FileNotFoundError):
            apply_desktop_wallpaper([Path("/nonexistent/video.mp4")])

    def test_successful_apply(
        self, sample_video: Path, mock_subprocess: MagicMock
    ) -> None:
        # Should not raise
        apply_desktop_wallpaper([sample_video])
        mock_subprocess.assert_called_once()

        # Verify qdbus was called
        args = mock_subprocess.call_args[0][0]
        assert args[0] == "qdbus"
        assert "org.kde.plasmashell" in args

    def test_qdbus_failure(
        self, sample_video: Path, mock_subprocess: MagicMock
    ) -> None:
        mock_subprocess.return_value.returncode = 1
        mock_subprocess.return_value.stderr = "connection refused"

        with pytest.raises(DBusError, match="qdbus command failed"):
            apply_desktop_wallpaper([sample_video])


class TestGetEvaluateScriptCommand:
    """Tests for command preview."""

    def test_returns_list(self, sample_video: Path) -> None:
        cmd = get_evaluate_script_command([sample_video])
        assert isinstance(cmd, list)
        assert cmd[0] == "qdbus"
        assert len(cmd) == 5
