"""Shared pytest fixtures for Livepaper tests."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from livepaper.models import AppConfig, WallpaperEntry


@pytest.fixture()
def tmp_config_dir(tmp_path: Path) -> Path:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir


@pytest.fixture()
def tmp_config_file(tmp_config_dir: Path) -> Path:
    return tmp_config_dir / "config.json"


@pytest.fixture()
def sample_video(tmp_path: Path) -> Path:
    video = tmp_path / "test_video.mp4"
    video.write_bytes(b"\x00" * 1024)
    return video


@pytest.fixture()
def sample_wallpaper_entry(sample_video: Path) -> WallpaperEntry:
    return WallpaperEntry(path=sample_video, name="test_video")


@pytest.fixture()
def sample_config(sample_wallpaper_entry: WallpaperEntry) -> AppConfig:
    return AppConfig(wallpapers=[sample_wallpaper_entry])


@pytest.fixture()
def mock_subprocess(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    mock_run = MagicMock()
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = ""
    mock_run.return_value.stderr = ""
    monkeypatch.setattr("subprocess.run", mock_run)
    return mock_run
