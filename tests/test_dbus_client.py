"""Tests for DBus client service."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from livepaper.models import BlurMode, FillMode, PauseMode, PlaybackConfig, VideoConfig
from livepaper.services.dbus_client import (
    PLUGIN_ID,
    DBusError,
    _build_wallpaper_script,
    _get_qdbus_binary,
    _sanitize_path,
    apply_desktop_wallpaper,
    get_evaluate_script_command,
)


class TestPluginId:
    """Ensure the plugin ID is exactly right — wrong ID causes a silent black screen."""

    def test_plugin_id_is_full_id(self) -> None:
        # The plugin ID must be the full dotted name, NOT the short 'smart-video-wallpaper-reborn'
        assert PLUGIN_ID == "luisbocanegra.smart.video.wallpaper.reborn"
        assert "." in PLUGIN_ID
        assert not PLUGIN_ID.startswith("smart-")


class TestGetQdbusBinary:
    """qdbus binary detection."""

    def test_returns_string(self) -> None:
        result = _get_qdbus_binary()
        assert isinstance(result, str)
        assert "qdbus" in result


class TestSanitizePath:
    def test_normal_path(self, sample_video: Path) -> None:
        result = _sanitize_path(sample_video)
        assert str(sample_video.resolve()) in result or result == str(sample_video.resolve())

    def test_path_with_quotes(self, tmp_path: Path) -> None:
        video = tmp_path / "it's a video.mp4"
        video.write_bytes(b"\x00")
        result = _sanitize_path(video)
        assert "\\'" in result

    def test_path_with_spaces(self, tmp_path: Path) -> None:
        video = tmp_path / "my video file.mp4"
        video.write_bytes(b"\x00")
        result = _sanitize_path(video)
        assert "my video file" in result


class TestBuildWallpaperScript:
    """Script generation must use the correct plugin ID and all config keys."""

    def test_uses_correct_plugin_id(self, sample_video: Path) -> None:
        script = _build_wallpaper_script([sample_video])
        assert PLUGIN_ID in script
        # Must NOT contain the short/wrong ID
        assert "wallpaperPlugin = \"smart-video-wallpaper-reborn\"" not in script

    def test_config_group_uses_correct_plugin_id(self, sample_video: Path) -> None:
        script = _build_wallpaper_script([sample_video])
        # The config group Array must also use the full plugin ID
        assert f'"{PLUGIN_ID}"' in script

    def test_single_video_url(self, sample_video: Path) -> None:
        script = _build_wallpaper_script([sample_video])
        assert "VideoUrls" in script
        assert '\\"filename\\":\\"file://' in script

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
        assert "true" in script  # screen_filter is 'true' for all screens

    def test_video_config_written(self, sample_video: Path) -> None:
        vc = VideoConfig(
            fill_mode=FillMode.PRESERVE_ASPECT_FIT,
            pause_mode=PauseMode.ACTIVE_WINDOW,
            blur_mode=BlurMode.MAXIMIZED_OR_FULLSCREEN,
            blur_radius=60,
            blur_on_original_proportions=False,
            battery_threshold=30,
            check_windows_from_all_screens=True,
        )
        script = _build_wallpaper_script([sample_video], video_config=vc)
        assert "FillMode" in script
        assert "PauseMode" in script
        assert "BlurMode" in script
        assert "BlurRadius" in script
        assert "PauseBatteryLevel" in script
        assert "FillBlur" in script
        assert "CheckWindowsActiveScreen" in script
        assert "30" in script  # battery threshold value
        assert 'd.writeConfig("PauseMode", 1);' in script
        assert 'd.writeConfig("BlurMode", 0);' in script
        assert 'd.writeConfig("FillBlur", false);' in script
        assert 'd.writeConfig("CheckWindowsActiveScreen", false);' in script

    def test_playback_config_written(self, sample_video: Path) -> None:
        pc = PlaybackConfig(
            volume=75,
            mute_audio=True,
            playback_rate=1.5,
            random_order=True,
            resume_time=True,
            loop_current_video=True,
            timer=125,
            fade_enabled=True,
            fade_duration=2000,
        )
        script = _build_wallpaper_script([sample_video], playback_config=pc)
        assert "Volume" in script
        assert "PlaybackRate" in script
        assert "AlternativePlaybackRate" in script
        assert "MuteMode" in script
        assert "RandomMode" in script
        assert "ResumeLastVideo" in script
        assert "CrossfadeEnabled" in script
        assert "CrossfadeDuration" in script
        assert "ChangeWallpaperMode" in script
        assert "2000" in script
        assert 'd.writeConfig("Volume", 0.75);' in script
        assert 'd.writeConfig("MuteMode", 5);' in script
        assert 'd.writeConfig("RandomMode", true);' in script
        assert 'd.writeConfig("ResumeLastVideo", true);' in script
        assert 'd.writeConfig("ChangeWallpaperMode", 2);' in script
        assert 'd.writeConfig("ChangeWallpaperTimerMinutes", 2);' in script
        assert 'd.writeConfig("ChangeWallpaperTimerSeconds", 5);' in script
        assert '\\"loop\\":true' in script


class TestApplyDesktopWallpaper:
    def test_file_not_found_raises(self) -> None:
        with pytest.raises(FileNotFoundError):
            apply_desktop_wallpaper([Path("/nonexistent/video.mp4")])

    def test_successful_apply_calls_qdbus(self, sample_video: Path, mock_subprocess: MagicMock) -> None:
        apply_desktop_wallpaper([sample_video])
        mock_subprocess.assert_called_once()
        args = mock_subprocess.call_args[0][0]
        assert "qdbus" in args[0]
        assert "org.kde.plasmashell" in args

    def test_qdbus_failure_raises_dbus_error(self, sample_video: Path, mock_subprocess: MagicMock) -> None:
        mock_subprocess.return_value.returncode = 1
        mock_subprocess.return_value.stderr = "connection refused"
        with pytest.raises(DBusError, match="qdbus command failed"):
            apply_desktop_wallpaper([sample_video])

    def test_passes_video_config(self, sample_video: Path, mock_subprocess: MagicMock) -> None:
        vc = VideoConfig(fill_mode=FillMode.STRETCH)
        apply_desktop_wallpaper([sample_video], video_config=vc)
        # Script passed as last arg; check it has FillMode
        script_arg = mock_subprocess.call_args[0][0][-1]
        assert "FillMode" in script_arg

    def test_passes_playback_config(self, sample_video: Path, mock_subprocess: MagicMock) -> None:
        pc = PlaybackConfig(volume=50, mute_audio=True)
        apply_desktop_wallpaper([sample_video], playback_config=pc)
        script_arg = mock_subprocess.call_args[0][0][-1]
        assert "Volume" in script_arg
        assert "MuteMode" in script_arg


class TestGetEvaluateScriptCommand:
    def test_returns_list_with_correct_structure(self, sample_video: Path) -> None:
        cmd = get_evaluate_script_command([sample_video])
        assert isinstance(cmd, list)
        assert len(cmd) == 5
        assert "qdbus" in cmd[0]
        assert cmd[1] == "org.kde.plasmashell"
        assert cmd[2] == "/PlasmaShell"
        # Script (last arg) must contain the correct plugin ID
        assert PLUGIN_ID in cmd[-1]
