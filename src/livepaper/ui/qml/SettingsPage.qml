import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: settingsPage
    
    // Store local state
    property var configData: ({})
    
    Connections {
        target: appBridge
        function onConfigChanged() {
            settingsPage.loadConfig()
        }
    }
    
    Component.onCompleted: {
        loadConfig()
    }
    
    function loadConfig() {
        configData = appBridge.getConfig()
        
        // Populate fields
        pauseCombo.currentIndex = pauseCombo.indexOfValue(configData["pause_condition"] || "fullscreen")
        muteCheck.checked = configData["mute_by_default"] || false
        speedSlider.value = (configData["playback_speed"] || 1.0) * 100
        
        blurCheck.checked = configData["blur_enabled"] || false
        blurSlider.value = configData["blur_radius"] !== undefined ? configData["blur_radius"] : 40
        
        batteryCheck.checked = configData["battery_saver_enabled"] !== undefined ? configData["battery_saver_enabled"] : true
        batterySlider.value = configData["battery_threshold"] !== undefined ? configData["battery_threshold"] : 20
        
        lockSyncCheck.checked = configData["sync_lock_screen"] || false
        
        monitorCombo.currentIndex = monitorCombo.indexOfValue(configData["monitor_mode"] || "all")
    }
    
    function saveConfig() {
        var newConfig = {
            "pause_condition": pauseCombo.currentValue,
            "mute_by_default": muteCheck.checked,
            "playback_speed": speedSlider.value / 100.0,
            "blur_enabled": blurCheck.checked,
            "blur_radius": blurSlider.value,
            "battery_saver_enabled": batteryCheck.checked,
            "battery_threshold": batterySlider.value,
            "sync_lock_screen": lockSyncCheck.checked,
            "monitor_mode": monitorCombo.currentValue
        }
        appBridge.saveConfig(newConfig)
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 32
        spacing: 24

        Label {
            text: "Settings"
            font.pixelSize: 28
            font.bold: true
            color: "white"
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true

            ColumnLayout {
                width: parent.width - 24
                spacing: 32

                // Playback
                ColumnLayout {
                    spacing: 12
                    Label { text: "Playback"; color: "#00FFA3"; font.bold: true; font.pixelSize: 16 }
                    
                    RowLayout {
                        Label { text: "Pause video when:"; color: "white" }
                        ComboBox {
                            id: pauseCombo
                            textRole: "text"
                            valueRole: "value"
                            model: [
                                {text: "Never", value: "never"},
                                {text: "Fullscreen", value: "fullscreen"},
                                {text: "Maximized", value: "maximized"},
                                {text: "Active Window", value: "active_window"}
                            ]
                        }
                    }
                    
                    CheckBox {
                        id: muteCheck
                        text: "Mute audio by default"
                        contentItem: Text {
                            text: muteCheck.text
                            color: "white"
                            leftPadding: muteCheck.indicator.width + muteCheck.spacing
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                    
                    RowLayout {
                        Label { text: "Playback speed:"; color: "white" }
                        Slider {
                            id: speedSlider
                            from: 25; to: 400; stepSize: 25
                        }
                        Label { text: (speedSlider.value / 100.0).toFixed(2) + "x"; color: "#8A8D98" }
                    }
                }

                // Blur
                ColumnLayout {
                    spacing: 12
                    Label { text: "Blur Effect"; color: "#00FFA3"; font.bold: true; font.pixelSize: 16 }
                    
                    CheckBox {
                        id: blurCheck
                        text: "Enable blur effect"
                        contentItem: Text {
                            text: blurCheck.text
                            color: "white"
                            leftPadding: blurCheck.indicator.width + blurCheck.spacing
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                    
                    RowLayout {
                        Label { text: "Blur radius:"; color: "white" }
                        Slider {
                            id: blurSlider
                            from: 0; to: 100; stepSize: 10
                        }
                        Label { text: blurSlider.value; color: "#8A8D98" }
                    }
                }
                
                // Battery
                ColumnLayout {
                    spacing: 12
                    Label { text: "Battery Saver"; color: "#00FFA3"; font.bold: true; font.pixelSize: 16 }
                    
                    CheckBox {
                        id: batteryCheck
                        text: "Pause video on low battery"
                        contentItem: Text {
                            text: batteryCheck.text
                            color: "white"
                            leftPadding: batteryCheck.indicator.width + batteryCheck.spacing
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                    
                    RowLayout {
                        Label { text: "Threshold:"; color: "white" }
                        Slider {
                            id: batterySlider
                            from: 5; to: 100; stepSize: 5
                        }
                        Label { text: batterySlider.value + "%"; color: "#8A8D98" }
                    }
                }
                
                // Lock Screen
                ColumnLayout {
                    spacing: 12
                    Label { text: "Lock Screen"; color: "#00FFA3"; font.bold: true; font.pixelSize: 16 }
                    
                    CheckBox {
                        id: lockSyncCheck
                        text: "Sync desktop wallpaper to lock screen"
                        contentItem: Text {
                            text: lockSyncCheck.text
                            color: "white"
                            leftPadding: lockSyncCheck.indicator.width + lockSyncCheck.spacing
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                }
                
                // Monitors
                ColumnLayout {
                    spacing: 12
                    Label { text: "Monitors"; color: "#00FFA3"; font.bold: true; font.pixelSize: 16 }
                    
                    RowLayout {
                        Label { text: "Apply wallpaper to:"; color: "white" }
                        ComboBox {
                            id: monitorCombo
                            textRole: "text"
                            valueRole: "value"
                            model: [
                                {text: "All", value: "all"},
                                {text: "Per Screen", value: "per_screen"}
                            ]
                        }
                    }
                }
            }
        }
        
        RowLayout {
            Layout.fillWidth: true
            Item { Layout.fillWidth: true } // spring
            
            Button {
                id: saveBtn
                text: "Save Settings"
                font.bold: true
                
                contentItem: Text {
                    text: saveBtn.text
                    font: saveBtn.font
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                
                background: Rectangle {
                    implicitWidth: 140
                    implicitHeight: 40
                    color: saveBtn.down ? Qt.darker("#228be6", 1.2) : "#228be6"
                    radius: 8
                }
                
                onClicked: settingsPage.saveConfig()
            }
        }
    }
}
