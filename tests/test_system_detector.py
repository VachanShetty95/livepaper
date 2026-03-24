"""Tests for system detector service."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from livepaper.services.system_detector import (
    detect_codecs_available,
    detect_plasma_version,
    detect_plugin_installed,
    detect_system_status,
)


class TestDetectPlasmaVersion:
    def test_plasma_6_detected(self, mock_subprocess: MagicMock) -> None:
        mock_subprocess.return_value.stdout = "plasmashell 6.1.4"
        is_ok, version = detect_plasma_version()
        assert is_ok is True
        assert version == "6.1.4"

    def test_plasma_5_too_old(self, mock_subprocess: MagicMock) -> None:
        mock_subprocess.return_value.stdout = "plasmashell 5.27.11"
        is_ok, version = detect_plasma_version()
        assert is_ok is False
        assert version == "5.27.11"

    def test_plasmashell_not_found(self, mock_subprocess: MagicMock) -> None:
        mock_subprocess.side_effect = FileNotFoundError()
        is_ok, version = detect_plasma_version()
        assert is_ok is False
        assert version == ""

    def test_command_fails(self, mock_subprocess: MagicMock) -> None:
        mock_subprocess.return_value.returncode = 1
        mock_subprocess.return_value.stdout = ""
        is_ok, version = detect_plasma_version()
        assert is_ok is False
        assert version == ""

    def test_malformed_output(self, mock_subprocess: MagicMock) -> None:
        mock_subprocess.return_value.stdout = "something weird"
        is_ok, _version = detect_plasma_version()
        assert is_ok is False


class TestDetectPluginInstalled:
    def test_via_pacman(self, mock_subprocess: MagicMock) -> None:
        mock_subprocess.return_value.stdout = "Name: plasma6-wallpapers..."
        assert detect_plugin_installed() is True

    def test_not_installed(self, mock_subprocess: MagicMock) -> None:
        mock_subprocess.return_value.returncode = 1
        mock_subprocess.return_value.stdout = ""
        result = detect_plugin_installed()
        assert isinstance(result, bool)


class TestDetectCodecsAvailable:
    def test_via_pacman(self, mock_subprocess: MagicMock) -> None:
        mock_subprocess.return_value.stdout = "Name: qt6-multimedia-ffmpeg"
        assert detect_codecs_available() is True

    def test_fallback_ffmpeg(self, mock_subprocess: MagicMock) -> None:
        mock_subprocess.return_value.returncode = 1
        mock_subprocess.return_value.stdout = ""
        with patch("livepaper.services.system_detector.shutil.which", return_value="/usr/bin/ffmpeg"):
            assert detect_codecs_available() is True

    def test_nothing_found(self, mock_subprocess: MagicMock) -> None:
        mock_subprocess.return_value.returncode = 1
        mock_subprocess.return_value.stdout = ""
        with patch("livepaper.services.system_detector.shutil.which", return_value=None):
            assert detect_codecs_available() is False


class TestDetectSystemStatus:
    def test_returns_system_status(self, mock_subprocess: MagicMock) -> None:
        mock_subprocess.return_value.stdout = "plasmashell 6.1.0"
        status = detect_system_status()
        assert status.plasma_ok is True
        assert status.plasma_version == "6.1.0"
