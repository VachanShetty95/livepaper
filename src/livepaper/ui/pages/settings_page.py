"""Settings page — exposes every option the plugin supports.

Organised into the same sections the plugin uses:
  Videos → Playback → Desktop Effects → Battery/Power
"""

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
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from livepaper.models import (
    AppConfig,
    BlurMode,
    FillMode,
    MonitorMode,
    PauseMode,
    PlaybackConfig,
    VideoConfig,
)
from livepaper.services.wallpaper_service import WallpaperService


class SettingsPage(QWidget):
    """Application settings form covering all plugin options."""

    def __init__(
        self,
        service: WallpaperService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._service = service
        self._setup_ui()
        self._load_settings()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.setSpacing(0)

        title = QLabel("Settings")
        title.setStyleSheet("font-size: 22px; font-weight: bold; margin-bottom: 16px;")
        outer.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(16)
        form_layout.setContentsMargins(0, 0, 12, 0)

        form_layout.addWidget(self._build_video_group())
        form_layout.addWidget(self._build_playback_group())
        form_layout.addWidget(self._build_blur_group())
        form_layout.addWidget(self._build_pause_group())
        form_layout.addWidget(self._build_battery_group())
        form_layout.addWidget(self._build_lockscreen_group())
        form_layout.addWidget(self._build_monitor_group())
        form_layout.addStretch(1)

        scroll.setWidget(form_widget)
        outer.addWidget(scroll, 1)
        outer.addLayout(self._build_footer())

    def _group(self, title: str) -> tuple[QGroupBox, QFormLayout]:
        box = QGroupBox(title)
        form = QFormLayout(box)
        form.setSpacing(10)
        form.setContentsMargins(16, 12, 16, 12)
        return box, form

    def _labeled_slider(
        self,
        minimum: int,
        maximum: int,
        suffix: str = "",
        tick_interval: int = 0,
    ) -> tuple[QHBoxLayout, QSlider, QLabel]:
        layout = QHBoxLayout()
        layout.setSpacing(8)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(minimum)
        slider.setMaximum(maximum)
        if tick_interval:
            slider.setTickInterval(tick_interval)
            slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        label = QLabel()
        label.setFixedWidth(52)
        label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        def _update(v: int) -> None:
            label.setText(f"{v}{suffix}")

        slider.valueChanged.connect(_update)
        layout.addWidget(slider)
        layout.addWidget(label)
        return layout, slider, label

    # ------------------------------------------------------------------
    # Section builders
    # ------------------------------------------------------------------

    def _build_video_group(self) -> QGroupBox:
        box, form = self._group("Videos")

        self._fill_mode_combo = QComboBox()
        for mode in FillMode:
            self._fill_mode_combo.addItem(mode.label, mode)
        form.addRow("Positioning:", self._fill_mode_combo)

        return box

    def _build_playback_group(self) -> QGroupBox:
        box, form = self._group("Playback")

        # Speed
        speed_layout, self._speed_slider, self._speed_label = self._labeled_slider(
            10, 400, "x", 50
        )
        # Display as decimal: stored as 10-400, shown as 0.10-4.00
        self._speed_slider.valueChanged.connect(
            lambda v: self._speed_label.setText(f"{v / 100:.2f}x")
        )
        form.addRow("Speed:", speed_layout)

        # Alternative speed
        alt_speed_layout, self._alt_speed_slider, self._alt_speed_label = self._labeled_slider(
            10, 400, "x", 50
        )
        self._alt_speed_slider.valueChanged.connect(
            lambda v: self._alt_speed_label.setText(f"{v / 100:.2f}x")
        )
        form.addRow("Alt speed:", alt_speed_layout)

        # Volume
        vol_layout, self._volume_slider, self._volume_label = self._labeled_slider(0, 100, "%", 10)
        form.addRow("Volume:", vol_layout)

        # Mute
        self._mute_check = QCheckBox("Mute audio")
        form.addRow("", self._mute_check)

        # Random order
        self._random_check = QCheckBox("Random playback order")
        form.addRow("", self._random_check)

        # Resume last position on startup
        self._resume_check = QCheckBox("Resume last position on startup")
        form.addRow("", self._resume_check)

        # Timer (switch video every N seconds; 0 = play full length)
        timer_layout = QHBoxLayout()
        timer_layout.setSpacing(8)
        self._timer_spin = QSpinBox()
        self._timer_spin.setMinimum(0)
        self._timer_spin.setMaximum(86400)
        self._timer_spin.setSingleStep(5)
        self._timer_spin.setSpecialValueText("Off (play full length)")
        self._timer_spin.setSuffix(" s")
        self._timer_spin.setFixedWidth(180)
        timer_layout.addWidget(self._timer_spin)
        timer_layout.addStretch()
        form.addRow("Switch video every:", timer_layout)

        # Cross-fade (Beta)
        self._fade_check = QCheckBox("Enable cross-fade transition between videos  (Beta)")
        form.addRow("", self._fade_check)

        fade_dur_layout, self._fade_dur_slider, self._fade_dur_label = self._labeled_slider(
            100, 5000, " ms", 500
        )
        form.addRow("Fade duration:", fade_dur_layout)

        self._fade_check.toggled.connect(self._fade_dur_slider.setEnabled)

        return box

    def _build_pause_group(self) -> QGroupBox:
        box, form = self._group("Pause video")

        self._pause_mode_combo = QComboBox()
        for mode in PauseMode:
            self._pause_mode_combo.addItem(mode.label, mode)
        form.addRow("Pause when:", self._pause_mode_combo)

        hint = QLabel(
            "Screen off and screen lock always pause the video automatically."
        )
        hint.setStyleSheet("font-size: 11px; color: palette(mid);")
        hint.setWordWrap(True)
        form.addRow("", hint)

        return box

    def _build_blur_group(self) -> QGroupBox:
        box, form = self._group("Blur effect")

        self._blur_mode_combo = QComboBox()
        for mode in BlurMode:
            self._blur_mode_combo.addItem(mode.label, mode)
        form.addRow("Blur when:", self._blur_mode_combo)

        blur_r_layout, self._blur_radius_slider, self._blur_radius_label = self._labeled_slider(
            0, 100, "", 10
        )
        form.addRow("Blur radius:", blur_r_layout)

        blur_anim_layout, self._blur_anim_slider, self._blur_anim_label = self._labeled_slider(
            0, 2000, " ms", 200
        )
        form.addRow("Blur animation:", blur_anim_layout)

        self._blur_original_check = QCheckBox(
            "Blur background when video plays in original proportions"
        )
        form.addRow("", self._blur_original_check)

        return box

    def _build_battery_group(self) -> QGroupBox:
        box, form = self._group("Battery saver")

        self._battery_check = QCheckBox("Pause video and disable blur on low battery")
        form.addRow("", self._battery_check)

        bat_layout, self._battery_slider, self._battery_label = self._labeled_slider(
            5, 100, "%", 5
        )
        self._battery_check.toggled.connect(self._battery_slider.setEnabled)
        form.addRow("Pause below:", bat_layout)

        return box

    def _build_lockscreen_group(self) -> QGroupBox:
        box, form = self._group("Lock screen")

        self._sync_lock_check = QCheckBox("Apply same wallpaper to lock screen")
        self._sync_lock_check.setToolTip(
            "Writes to ~/.config/kscreenlockerrc with matching settings."
        )
        form.addRow("", self._sync_lock_check)

        return box

    def _build_monitor_group(self) -> QGroupBox:
        box, form = self._group("Monitors")

        self._monitor_combo = QComboBox()
        for mode in MonitorMode:
            self._monitor_combo.addItem(mode.value.replace("_", " ").title(), mode)
        form.addRow("Apply to:", self._monitor_combo)

        self._all_screens_check = QCheckBox(
            "Detect windows from all screens (not just the wallpaper's screen)"
        )
        form.addRow("", self._all_screens_check)

        return box

    def _build_footer(self) -> QHBoxLayout:
        footer = QHBoxLayout()
        footer.setContentsMargins(0, 12, 0, 0)
        footer.addStretch(1)

        reset_btn = QPushButton("Reset to defaults")
        reset_btn.clicked.connect(self._reset_settings)
        footer.addWidget(reset_btn)

        save_btn = QPushButton("Save settings")
        save_btn.setStyleSheet("""
            QPushButton {
                border-radius: 8px; padding: 10px 20px; font-size: 13px;
                font-weight: bold; background-color: #228be6; color: #ffffff; border: none;
            }
            QPushButton:hover { background-color: #339af0; }
        """)
        save_btn.clicked.connect(self._save_settings)
        footer.addWidget(save_btn)

        return footer

    # ------------------------------------------------------------------
    # Load / Save
    # ------------------------------------------------------------------

    def _load_settings(self) -> None:
        cfg = self._service.config
        vc = cfg.video
        pc = cfg.playback

        # Videos
        idx = self._fill_mode_combo.findData(vc.fill_mode)
        self._fill_mode_combo.setCurrentIndex(max(idx, 0))

        # Playback
        self._speed_slider.setValue(int(pc.playback_rate * 100))
        self._speed_label.setText(f"{pc.playback_rate:.2f}x")
        self._alt_speed_slider.setValue(int(pc.playback_rate_alt * 100))
        self._alt_speed_label.setText(f"{pc.playback_rate_alt:.2f}x")
        self._volume_slider.setValue(pc.volume)
        self._volume_label.setText(f"{pc.volume}%")
        self._mute_check.setChecked(pc.mute_audio)
        self._random_check.setChecked(pc.random_order)
        self._resume_check.setChecked(pc.resume_time)
        self._timer_spin.setValue(pc.timer)
        self._fade_check.setChecked(pc.fade_enabled)
        self._fade_dur_slider.setValue(pc.fade_duration)
        self._fade_dur_label.setText(f"{pc.fade_duration} ms")
        self._fade_dur_slider.setEnabled(pc.fade_enabled)

        # Pause
        idx = self._pause_mode_combo.findData(vc.pause_mode)
        self._pause_mode_combo.setCurrentIndex(max(idx, 0))

        # Blur
        idx = self._blur_mode_combo.findData(vc.blur_mode)
        self._blur_mode_combo.setCurrentIndex(max(idx, 0))
        self._blur_radius_slider.setValue(vc.blur_radius)
        self._blur_radius_label.setText(str(vc.blur_radius))
        self._blur_anim_slider.setValue(vc.blur_animation_duration)
        self._blur_anim_label.setText(f"{vc.blur_animation_duration} ms")
        self._blur_original_check.setChecked(vc.blur_on_original_proportions)

        # Battery
        self._battery_check.setChecked(vc.battery_saver_enabled)
        self._battery_slider.setValue(vc.battery_threshold)
        self._battery_label.setText(f"{vc.battery_threshold}%")
        self._battery_slider.setEnabled(vc.battery_saver_enabled)

        # Lock screen + monitors
        self._sync_lock_check.setChecked(cfg.sync_lock_screen)
        idx = self._monitor_combo.findData(cfg.monitor_mode)
        self._monitor_combo.setCurrentIndex(max(idx, 0))
        self._all_screens_check.setChecked(vc.check_windows_from_all_screens)

    def _save_settings(self) -> None:
        cfg = self._service.config
        updated = cfg.model_copy(
            update={
                "video": VideoConfig(
                    fill_mode=self._fill_mode_combo.currentData(),
                    pause_mode=self._pause_mode_combo.currentData(),
                    blur_mode=self._blur_mode_combo.currentData(),
                    blur_radius=self._blur_radius_slider.value(),
                    blur_animation_duration=self._blur_anim_slider.value(),
                    blur_on_original_proportions=self._blur_original_check.isChecked(),
                    battery_saver_enabled=self._battery_check.isChecked(),
                    battery_threshold=self._battery_slider.value(),
                    check_windows_from_all_screens=self._all_screens_check.isChecked(),
                ),
                "playback": PlaybackConfig(
                    mute_audio=self._mute_check.isChecked(),
                    volume=self._volume_slider.value(),
                    playback_rate=self._speed_slider.value() / 100.0,
                    playback_rate_alt=self._alt_speed_slider.value() / 100.0,
                    random_order=self._random_check.isChecked(),
                    resume_time=self._resume_check.isChecked(),
                    timer=self._timer_spin.value(),
                    fade_enabled=self._fade_check.isChecked(),
                    fade_duration=self._fade_dur_slider.value(),
                ),
                "sync_lock_screen": self._sync_lock_check.isChecked(),
                "monitor_mode": self._monitor_combo.currentData(),
            }
        )
        self._service.save_config(updated)
        QMessageBox.information(self, "Settings", "Settings saved.")

    def _reset_settings(self) -> None:
        reply = QMessageBox.question(
            self,
            "Reset settings",
            "Reset all settings to plugin defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            defaults = AppConfig(
                wallpapers=self._service.config.wallpapers,
                first_run_complete=self._service.config.first_run_complete,
            )
            self._service.save_config(defaults)
            self._load_settings()
