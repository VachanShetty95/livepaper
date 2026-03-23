"""Setup wizard page for first-run system health check."""

from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from livepaper.models import SystemCheckItem, SystemStatus
from livepaper.services.system_detector import detect_system_status
from livepaper.ui.utils import open_url


class _DetectionWorker(QThread):
    """Background thread for system detection."""

    finished = pyqtSignal(SystemStatus)

    def run(self) -> None:
        status = detect_system_status()
        self.finished.emit(status)


class _CheckRow(QFrame):
    """A single status row in the health check."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                border-radius: 8px;
                padding: 12px 16px;
                margin: 4px 0;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        self._icon_label = QLabel("⏳")
        self._icon_label.setFixedWidth(32)
        self._icon_label.setStyleSheet("font-size: 20px;")
        layout.addWidget(self._icon_label)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        self._name_label = QLabel()
        self._name_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        text_layout.addWidget(self._name_label)

        self._status_label = QLabel()
        self._status_label.setStyleSheet("font-size: 12px; opacity: 0.7;")
        text_layout.addWidget(self._status_label)

        layout.addLayout(text_layout, 1)

        self._fix_button = QPushButton("Fix")
        self._fix_button.setFixedWidth(80)
        self._fix_button.setVisible(False)
        self._fix_button.setStyleSheet("""
            QPushButton {
                border-radius: 6px;
                padding: 6px 16px;
                font-size: 12px;
                background-color: #e67700;
                color: #ffffff;
                border: none;
            }
            QPushButton:hover {
                background-color: #f08c00;
            }
        """)
        layout.addWidget(self._fix_button)

    def set_loading(self, name: str) -> None:
        """Show loading state."""
        self._name_label.setText(name)
        self._icon_label.setText("⏳")
        self._status_label.setText("Checking...")
        self._fix_button.setVisible(False)

    def set_result(self, item: SystemCheckItem) -> None:
        """Update with check result."""
        self._name_label.setText(item.name)

        if item.passed:
            self._icon_label.setText("✅")
            self._status_label.setText(item.message)
            self._fix_button.setVisible(False)
        else:
            self._icon_label.setText("⚠️")
            self._status_label.setText(item.message)
            if item.fix_url:
                self._fix_button.setVisible(True)
                self._fix_button.clicked.connect(
                    lambda _checked=False, url=item.fix_url: open_url(url)
                )


class SetupWizardPage(QWidget):
    """First-run setup wizard with system health checks."""

    def __init__(
        self,
        on_continue: Callable[[], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._on_continue = on_continue
        self._status: SystemStatus | None = None
        self._setup_ui()
        self._run_checks()

    def _setup_ui(self) -> None:
        """Build the wizard layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setSpacing(16)

        # Header
        title = QLabel("Welcome to Livepaper")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Let's make sure everything is set up correctly.")
        subtitle.setStyleSheet("font-size: 14px; opacity: 0.7;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(24)

        # Check rows
        self._check_rows: list[_CheckRow] = []
        check_names = [
            "KDE Plasma 6",
            "Smart Video Wallpaper Plugin",
            "Media Codecs (qt6-multimedia-ffmpeg)",
        ]
        for name in check_names:
            row = _CheckRow()
            row.set_loading(name)
            self._check_rows.append(row)
            layout.addWidget(row)

        layout.addStretch(1)

        # Footer buttons
        footer = QHBoxLayout()
        footer.addStretch(1)

        self._recheck_btn = QPushButton("Re-check")
        self._recheck_btn.setFixedWidth(120)
        self._recheck_btn.setStyleSheet("""
            QPushButton {
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 14px;
                background-color: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                color: palette(text);
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.14);
            }
        """)
        self._recheck_btn.clicked.connect(self._run_checks)
        footer.addWidget(self._recheck_btn)

        self._continue_btn = QPushButton("Continue →")
        self._continue_btn.setFixedWidth(140)
        self._continue_btn.setEnabled(False)
        self._continue_btn.setStyleSheet("""
            QPushButton {
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: bold;
                background-color: #228be6;
                color: #ffffff;
                border: none;
            }
            QPushButton:hover {
                background-color: #339af0;
            }
            QPushButton:disabled {
                background-color: rgba(255, 255, 255, 0.06);
                color: rgba(255, 255, 255, 0.3);
            }
        """)
        self._continue_btn.clicked.connect(self._on_continue_clicked)
        footer.addWidget(self._continue_btn)

        layout.addLayout(footer)

    def _run_checks(self) -> None:
        """Start system detection in a background thread."""
        self._continue_btn.setEnabled(False)
        for row in self._check_rows:
            row.set_loading(row._name_label.text())

        self._worker = _DetectionWorker()
        self._worker.finished.connect(self._on_checks_complete)
        self._worker.start()

    def _on_checks_complete(self, status: SystemStatus) -> None:
        """Handle detection results."""
        self._status = status
        items = status.to_check_items()

        for row, item in zip(self._check_rows, items, strict=True):
            row.set_result(item)

        self._continue_btn.setEnabled(status.all_checks_passed)

    def _on_continue_clicked(self) -> None:
        """Handle the continue button."""
        if self._on_continue:
            self._on_continue()
