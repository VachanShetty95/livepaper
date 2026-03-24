"""About page with app info and credits."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from livepaper import __app_name__, __version__
from livepaper.ui.utils import open_url


class AboutPage(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_label = QLabel("🎬")
        icon_label.setStyleSheet("font-size: 64px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        layout.addSpacing(16)

        name_label = QLabel(__app_name__)
        name_label.setStyleSheet("font-size: 28px; font-weight: bold;")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)

        version_label = QLabel(f"Version {__version__}")
        version_label.setStyleSheet("font-size: 14px; color: palette(mid);")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

        layout.addSpacing(24)

        desc = QLabel(
            "A polished video wallpaper manager for KDE Plasma 6.\n"
            "Built on top of Smart Video Wallpaper Reborn."
        )
        desc.setStyleSheet("font-size: 14px;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addSpacing(24)

        credits_label = QLabel("Plugin by Luis Bocanegra\nApp by Vachan Shetty")
        credits_label.setStyleSheet("font-size: 12px; color: palette(mid);")
        credits_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(credits_label)

        layout.addSpacing(16)

        license_label = QLabel("Licensed under the MIT License")
        license_label.setStyleSheet("font-size: 12px; color: palette(mid);")
        license_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(license_label)

        layout.addSpacing(24)

        for text, url in [
            ("📂  View on GitHub", "https://github.com/VachanShetty95/livepaper"),
            ("🔌  Plugin repository", "https://github.com/luisbocanegra/plasma-smart-video-wallpaper-reborn"),
        ]:
            btn = QPushButton(text)
            btn.setFixedWidth(220)
            btn.setStyleSheet("""
                QPushButton {
                    border-radius: 8px; padding: 10px 20px; font-size: 13px;
                    background-color: rgba(255,255,255,0.08);
                    border: 1px solid rgba(255,255,255,0.15); color: palette(text);
                }
                QPushButton:hover { background-color: rgba(255,255,255,0.14); }
            """)
            btn.clicked.connect(lambda _=False, u=url: open_url(u))
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch(1)
