"""Settings page with playback, blur, battery, and monitor options."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from livepaper.models import MonitorMode, PauseCondition
from livepaper.services.wallpaper_service import WallpaperService


class SettingsPage(QWidget):
    """Application settings form."""

    def __init__(
        self,
        service: WallpaperService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._service = service
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self) -> None:
        """Build the settings form layout."""
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)

        # Header
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        outer.addWidget(title)
        outer.addSpacing(16)

        # Scroll area for the form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(20)

        # --- Playback Section ---
        playback_group = QGroupBox("Playback")
        playback_form = QFormLayout(playback_group)
        playback_form.setSpacing(12)

        self._pause_combo = QComboBox()
        for cond in PauseCondition:
            self._pause_combo.addItem(
                cond.value.replace("_", " ").title(), cond.value
            )
        playback_form.addRow("Pause video when:", self._pause_combo)

        self._mute_check = QCheckBox("Mute audio by default")
        playback_form.addRow("", self._mute_check)

        speed_layout = QHBoxLayout()
        self._speed_slider = QSlider(Qt.Orientation.Horizontal)
        self._speed_slider.setMinimum(25)
        self._speed_slider.setMaximum(400)
        self._speed_slider.setTickInterval(25)
        self._speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._speed_label = QLabel("1.0x")
        self._speed_slider.valueChanged.connect(
            lambda v: self._speed_label.setText(f"{v / 100:.2f}x")
        )
        speed_layout.addWidget(self._speed_slider)
        speed_layout.addWidget(self._speed_label)
        playback_form.addRow("Playback speed:", speed_layout)

        form_layout.addWidget(playback_group)

        # --- Blur Section ---
        blur_group = QGroupBox("Blur Effect")
        blur_form = QFormLayout(blur_group)
        blur_form.setSpacing(12)

        self._blur_check = QCheckBox("Enable blur effect")
        blur_form.addRow("", self._blur_check)

        radius_layout = QHBoxLayout()
        self._blur_slider = QSlider(Qt.Orientation.Horizontal)
        self._blur_slider.setMinimum(0)
        self._blur_slider.setMaximum(100)
        self._blur_slider.setTickInterval(10)
        self._blur_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._blur_label = QLabel("40")
        self._blur_slider.valueChanged.connect(
            lambda v: self._blur_label.setText(str(v))
        )
        radius_layout.addWidget(self._blur_slider)
        radius_layout.addWidget(self._blur_label)
        blur_form.addRow("Blur radius:", radius_layout)

        form_layout.addWidget(blur_group)

        # --- Battery Section ---
        battery_group = QGroupBox("Battery Saver")
        battery_form = QFormLayout(battery_group)
        battery_form.setSpacing(12)

        self._battery_check = QCheckBox("Pause video on low battery")
        battery_form.addRow("", self._battery_check)

        threshold_layout = QHBoxLayout()
        self._battery_slider = QSlider(Qt.Orientation.Horizontal)
        self._battery_slider.setMinimum(5)
        self._battery_slider.setMaximum(100)
        self._battery_slider.setTickInterval(5)
        self._battery_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._battery_label = QLabel("20%")
        self._battery_slider.valueChanged.connect(
            lambda v: self._battery_label.setText(f"{v}%")
        )
        threshold_layout.addWidget(self._battery_slider)
        threshold_layout.addWidget(self._battery_label)
        battery_form.addRow("Threshold:", threshold_layout)

        form_layout.addWidget(battery_group)

        # --- Lock Screen Section ---
        lock_group = QGroupBox("Lock Screen")
        lock_form = QFormLayout(lock_group)

        self._sync_lock_check = QCheckBox(
            "Sync desktop wallpaper to lock screen"
        )
        lock_form.addRow("", self._sync_lock_check)

        form_layout.addWidget(lock_group)

        # --- Monitors Section ---
        monitor_group = QGroupBox("Monitors")
        monitor_form = QFormLayout(monitor_group)

        self._monitor_combo = QComboBox()
        for mode in MonitorMode:
            self._monitor_combo.addItem(
                mode.value.replace("_", " ").title(), mode.value
            )
        monitor_form.addRow("Apply wallpaper to:", self._monitor_combo)

        form_layout.addWidget(monitor_group)

        form_layout.addStretch(1)
        scroll.setWidget(form_widget)
        outer.addWidget(scroll, 1)

        # --- Footer Buttons ---
        footer = QHBoxLayout()
        footer.addStretch(1)

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setStyleSheet("""
            QPushButton {
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13px;
            }
        """)
        reset_btn.clicked.connect(self._reset_settings)
        footer.addWidget(reset_btn)

        save_btn = QPushButton("Save Settings")
        save_btn.setStyleSheet("""
            QPushButton {
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
            }
        """)
        save_btn.clicked.connect(self._save_settings)
        footer.addWidget(save_btn)

        outer.addLayout(footer)

    def _load_settings(self) -> None:
        """Load current config values into the form controls."""
        config = self._service.config

        # Playback
        idx = self._pause_combo.findData(config.pause_condition.value)
        if idx >= 0:
            self._pause_combo.setCurrentIndex(idx)
        self._mute_check.setChecked(config.mute_by_default)
        self._speed_slider.setValue(int(config.playback_speed * 100))

        # Blur
        self._blur_check.setChecked(config.blur_enabled)
        self._blur_slider.setValue(config.blur_radius)

        # Battery
        self._battery_check.setChecked(config.battery_saver_enabled)
        self._battery_slider.setValue(config.battery_threshold)

        # Lock screen
        self._sync_lock_check.setChecked(config.sync_lock_screen)

        # Monitors
        idx = self._monitor_combo.findData(config.monitor_mode.value)
        if idx >= 0:
            self._monitor_combo.setCurrentIndex(idx)

    def _save_settings(self) -> None:
        """Save form values to config."""
        config = self._service.config
        updated = config.model_copy(update={
            "pause_condition": PauseCondition(self._pause_combo.currentData()),
            "mute_by_default": self._mute_check.isChecked(),
            "playback_speed": self._speed_slider.value() / 100.0,
            "blur_enabled": self._blur_check.isChecked(),
            "blur_radius": self._blur_slider.value(),
            "battery_saver_enabled": self._battery_check.isChecked(),
            "battery_threshold": self._battery_slider.value(),
            "sync_lock_screen": self._sync_lock_check.isChecked(),
            "monitor_mode": MonitorMode(self._monitor_combo.currentData()),
        })
        self._service.save_config(updated)
        QMessageBox.information(self, "Settings", "Settings saved successfully.")

    def _reset_settings(self) -> None:
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Reset all settings to default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            from livepaper.models import AppConfig

            defaults = AppConfig(
                wallpapers=self._service.config.wallpapers,
                first_run_complete=self._service.config.first_run_complete,
            )
            self._service.save_config(defaults)
            self._load_settings()
