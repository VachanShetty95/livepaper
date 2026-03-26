import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: settingsPage

    property var configData: ({})
    property bool savedFlash: false

    readonly property color baseColor: "#0A0A0C"
    readonly property color panelColor: "#141519"
    readonly property color borderColor: "#2A2B30"
    readonly property color accentColor: "#00FFA3"
    readonly property color accentHoverColor: "#33FFB7"
    readonly property color mutedColor: "#8A8D98"
    readonly property color softTextColor: "#C9CBD3"
    readonly property color trackColor: "#22242B"

    readonly property var pauseOptions: [
        { text: "Never", value: 0 },
        { text: "Fullscreen or maximized", value: 1 },
        { text: "Active window", value: 2 },
        { text: "Any window visible", value: 3 },
        { text: "Desktop effect", value: 4 }
    ]
    readonly property var blurOptions: [
        { text: "Never", value: 0 },
        { text: "Always", value: 1 },
        { text: "Fullscreen or maximized", value: 2 },
        { text: "Active window", value: 3 },
        { text: "Any window visible", value: 4 },
        { text: "Video paused", value: 5 },
        { text: "Desktop effect", value: 6 }
    ]
    readonly property var monitorOptions: [
        { text: "All monitors", value: "all" },
        { text: "Per screen", value: "per_screen" }
    ]
    readonly property var sectionTags: [
        "Playback",
        "Blur",
        "Battery Saver",
        "Lock Screen",
        "Displays"
    ]

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
        var video = configData.video || {}
        var playback = configData.playback || {}

        pauseCombo.currentIndex = pauseCombo.indexOfValue(video.pause_mode !== undefined ? video.pause_mode : 1)
        muteSwitch.checked = playback.mute_audio || false
        speedSlider.value = playback.playback_rate !== undefined ? playback.playback_rate : 1.0

        blurCombo.currentIndex = blurCombo.indexOfValue(video.blur_mode !== undefined ? video.blur_mode : 0)
        blurSlider.value = video.blur_radius !== undefined ? video.blur_radius : 40

        batterySwitch.checked = video.battery_saver_enabled !== undefined ? video.battery_saver_enabled : true
        batterySlider.value = video.battery_threshold !== undefined ? video.battery_threshold : 20

        lockSyncSwitch.checked = configData.sync_lock_screen || false

        monitorCombo.currentIndex = monitorCombo.indexOfValue(configData.monitor_mode || "all")
    }

    function saveConfig() {
        var newConfig = {
            "video": {
                "pause_mode": pauseCombo.currentValue,
                "blur_mode": blurCombo.currentValue,
                "blur_radius": Math.round(blurSlider.value),
                "battery_saver_enabled": batterySwitch.checked,
                "battery_threshold": Math.round(batterySlider.value)
            },
            "playback": {
                "mute_audio": muteSwitch.checked,
                "playback_rate": Number(speedSlider.value.toFixed(2))
            },
            "sync_lock_screen": lockSyncSwitch.checked,
            "monitor_mode": monitorCombo.currentValue
        }
        appBridge.saveConfig(newConfig)
        savedFlash = true
        saveFlashTimer.restart()
    }

    Timer {
        id: saveFlashTimer
        interval: 1800
        repeat: false
        onTriggered: settingsPage.savedFlash = false
    }

    component SettingsCard: Rectangle {
        id: card

        required property string eyebrow
        required property string title
        required property string description
        default property alias content: contentColumn.data

        Layout.fillWidth: true
        Layout.alignment: Qt.AlignTop
        implicitHeight: cardLayout.implicitHeight + 40
        radius: 18
        color: settingsPage.panelColor
        border.color: settingsPage.borderColor
        border.width: 1

        ColumnLayout {
            id: cardLayout

            anchors.fill: parent
            anchors.margins: 20
            spacing: 20

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6

                Label {
                    text: card.eyebrow
                    color: settingsPage.mutedColor
                    font.pixelSize: 11
                    font.bold: true
                    font.letterSpacing: 1.4
                }

                Label {
                    text: card.title
                    color: "white"
                    font.pixelSize: 20
                    font.bold: true
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }

                Text {
                    text: card.description
                    color: settingsPage.mutedColor
                    font.pixelSize: 13
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
            }

            ColumnLayout {
                id: contentColumn
                Layout.fillWidth: true
                spacing: 18
            }
        }
    }

    component ThemedComboBox: ComboBox {
        id: control

        implicitHeight: 44
        font.pixelSize: 14

        background: Rectangle {
            color: settingsPage.baseColor
            border.color: control.popup.visible || control.hovered ? settingsPage.accentColor : settingsPage.borderColor
            border.width: 1
            radius: 10
        }

        contentItem: Text {
            text: control.displayText
            color: "white"
            verticalAlignment: Text.AlignVCenter
            leftPadding: 14
            rightPadding: 36
            elide: Text.ElideRight
            font: control.font
        }

        indicator: Text {
            text: "\u25BE"
            color: settingsPage.mutedColor
            font.pixelSize: 11
            anchors.right: parent.right
            anchors.rightMargin: 14
            anchors.verticalCenter: parent.verticalCenter
        }

        delegate: ItemDelegate {
            width: ListView.view ? ListView.view.width : control.width
            highlighted: control.highlightedIndex === index

            background: Rectangle {
                radius: 8
                color: parent.highlighted ? "#173127" : "transparent"
            }

            contentItem: Text {
                text: modelData[control.textRole]
                color: "white"
                elide: Text.ElideRight
                verticalAlignment: Text.AlignVCenter
                font.pixelSize: 14
            }

            onClicked: {
                control.currentIndex = index
                control.popup.close()
            }
        }

        popup: Popup {
            y: control.height + 8
            width: control.width
            padding: 8

            background: Rectangle {
                color: settingsPage.panelColor
                border.color: settingsPage.borderColor
                border.width: 1
                radius: 12
            }

            contentItem: ListView {
                clip: true
                implicitHeight: contentHeight
                model: control.popup.visible ? control.delegateModel : null
                currentIndex: control.highlightedIndex
                ScrollBar.vertical: ScrollBar {
                    policy: ScrollBar.AsNeeded
                }
            }
        }
    }

    component ThemedSwitch: Switch {
        id: control

        implicitWidth: 46
        implicitHeight: 26
        padding: 0
        spacing: 0

        indicator: Rectangle {
            implicitWidth: 46
            implicitHeight: 26
            x: 0
            y: Math.round((control.availableHeight - height) / 2)
            radius: 13
            color: control.checked ? settingsPage.accentColor : settingsPage.trackColor
            border.color: control.checked ? settingsPage.accentColor : settingsPage.mutedColor

            Rectangle {
                x: control.checked ? parent.width - width - 3 : 3
                y: 3
                width: 20
                height: 20
                radius: 10
                color: control.checked ? settingsPage.baseColor : settingsPage.mutedColor

                Behavior on x {
                    NumberAnimation {
                        duration: 150
                        easing.type: Easing.OutCubic
                    }
                }
            }
        }

        contentItem: Item {
            implicitWidth: control.implicitWidth
            implicitHeight: control.implicitHeight
        }
    }

    component ThemedSlider: Slider {
        id: control

        implicitHeight: 20

        background: Rectangle {
            x: control.leftPadding
            y: control.topPadding + control.availableHeight / 2 - height / 2
            width: control.availableWidth
            height: 6
            radius: 3
            color: settingsPage.trackColor

            Rectangle {
                width: control.visualPosition * parent.width
                height: parent.height
                radius: 3
                color: control.enabled ? settingsPage.accentColor : settingsPage.borderColor
            }
        }

        handle: Rectangle {
            x: control.leftPadding + control.visualPosition * (control.availableWidth - width)
            y: control.topPadding + control.availableHeight / 2 - height / 2
            implicitWidth: 20
            implicitHeight: 20
            radius: 10
            color: control.pressed ? settingsPage.accentHoverColor : settingsPage.accentColor
            opacity: control.enabled ? 1 : 0.5
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 32
        spacing: 24

        RowLayout {
            Layout.fillWidth: true

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6

                Label {
                    text: "Settings"
                    font.pixelSize: 28
                    font.bold: true
                    color: "white"
                }

                Text {
                    text: "Shape how wallpapers behave across playback, blur, battery and display sync."
                    color: settingsPage.mutedColor
                    font.pixelSize: 14
                }
            }

            Button {
                id: saveBtn
                text: settingsPage.savedFlash ? "Saved" : "Save Settings"
                font.pixelSize: 14
                font.bold: true

                contentItem: Text {
                    text: saveBtn.text
                    font: saveBtn.font
                    color: "#0A0A0C"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }

                background: Rectangle {
                    implicitWidth: 156
                    implicitHeight: 40
                    color: saveBtn.hovered ? settingsPage.accentHoverColor : settingsPage.accentColor
                    radius: 20
                }

                onClicked: settingsPage.saveConfig()
            }
        }

        ScrollView {
            id: settingsScroll
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            contentWidth: availableWidth
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

            Item {
                width: settingsScroll.availableWidth
                implicitHeight: settingsContent.implicitHeight

                ColumnLayout {
                    id: settingsContent

                    width: parent.width
                    spacing: 24

                    Rectangle {
                        Layout.fillWidth: true
                        implicitHeight: heroContent.implicitHeight + 48
                        radius: 20
                        border.color: "#214338"
                        border.width: 1
                        gradient: Gradient {
                            GradientStop { position: 0.0; color: "#143428" }
                            GradientStop { position: 0.6; color: "#141519" }
                            GradientStop { position: 1.0; color: "#101114" }
                        }

                        ColumnLayout {
                            id: heroContent

                            anchors.fill: parent
                            anchors.margins: 24
                            spacing: 18

                            Label {
                                text: "GLOBAL CONTROLS"
                                color: settingsPage.mutedColor
                                font.pixelSize: 12
                                font.bold: true
                                font.letterSpacing: 1.5
                            }

                            Label {
                                text: "Keep the settings tab consistent with the wallpapers experience."
                                color: "white"
                                font.pixelSize: 22
                                font.bold: true
                                wrapMode: Text.WordWrap
                                Layout.fillWidth: true
                            }

                            Text {
                                text: "The same dark cards, mint accents and compact controls now carry through playback, blur, battery and sync preferences."
                                color: settingsPage.softTextColor
                                font.pixelSize: 14
                                wrapMode: Text.WordWrap
                                Layout.fillWidth: true
                            }

                            Flow {
                                Layout.fillWidth: true
                                spacing: 10

                                Repeater {
                                    model: settingsPage.sectionTags

                                    delegate: Rectangle {
                                        width: tagLabel.implicitWidth + 24
                                        height: 32
                                        radius: 16
                                        color: "#0F1613"
                                        border.color: "#214338"
                                        border.width: 1

                                        Text {
                                            id: tagLabel

                                            anchors.centerIn: parent
                                            text: modelData
                                            color: settingsPage.accentColor
                                            font.pixelSize: 12
                                            font.bold: true
                                        }
                                    }
                                }
                            }
                        }
                    }

                    GridLayout {
                        Layout.fillWidth: true
                        columns: width >= 980 ? 2 : 1
                        columnSpacing: 24
                        rowSpacing: 24

                        SettingsCard {
                            eyebrow: "PLAYBACK"
                            title: "Pause and sound defaults"
                            description: "Choose when playback backs off and what audio state new wallpapers should start with."

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 10

                                Label {
                                    text: "Pause video when"
                                    color: "white"
                                    font.pixelSize: 14
                                    font.bold: true
                                }

                                ThemedComboBox {
                                    id: pauseCombo
                                    Layout.fillWidth: true
                                    textRole: "text"
                                    valueRole: "value"
                                    model: settingsPage.pauseOptions
                                }
                            }

                            Rectangle {
                                Layout.fillWidth: true
                                radius: 12
                                color: settingsPage.baseColor
                                border.color: settingsPage.borderColor
                                border.width: 1
                                implicitHeight: 72

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 16
                                    spacing: 12

                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        spacing: 4

                                        Label {
                                            text: "Mute audio by default"
                                            color: "white"
                                            font.pixelSize: 14
                                            font.bold: true
                                        }

                                        Text {
                                            text: "Applies to new wallpaper sessions unless you change it later from the inspector."
                                            color: settingsPage.mutedColor
                                            font.pixelSize: 12
                                            wrapMode: Text.WordWrap
                                            Layout.fillWidth: true
                                        }
                                    }

                                    ThemedSwitch {
                                        id: muteSwitch
                                        Layout.alignment: Qt.AlignVCenter
                                    }
                                }
                            }

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 10

                                RowLayout {
                                    Layout.fillWidth: true

                                    Label {
                                        text: "Playback speed"
                                        color: "white"
                                        font.pixelSize: 14
                                        font.bold: true
                                    }

                                    Item {
                                        Layout.fillWidth: true
                                    }

                                    Label {
                                        text: speedSlider.value.toFixed(2) + "x"
                                        color: settingsPage.accentColor
                                        font.pixelSize: 14
                                        font.bold: true
                                    }
                                }

                                ThemedSlider {
                                    id: speedSlider
                                    Layout.fillWidth: true
                                    from: 0.1
                                    to: 4.0
                                    stepSize: 0.05
                                }
                            }
                        }

                        SettingsCard {
                            eyebrow: "BLUR"
                            title: "Backdrop treatment"
                            description: "Control when blur appears and how strong it should feel whenever the plugin renders it."

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 10

                                Label {
                                    text: "Blur mode"
                                    color: "white"
                                    font.pixelSize: 14
                                    font.bold: true
                                }

                                ThemedComboBox {
                                    id: blurCombo
                                    Layout.fillWidth: true
                                    textRole: "text"
                                    valueRole: "value"
                                    model: settingsPage.blurOptions
                                }
                            }

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 10
                                enabled: blurCombo.currentValue !== 0
                                opacity: enabled ? 1 : 0.5

                                RowLayout {
                                    Layout.fillWidth: true

                                    Label {
                                        text: "Blur radius"
                                        color: "white"
                                        font.pixelSize: 14
                                        font.bold: true
                                    }

                                    Item {
                                        Layout.fillWidth: true
                                    }

                                    Label {
                                        text: Math.round(blurSlider.value).toString()
                                        color: settingsPage.accentColor
                                        font.pixelSize: 14
                                        font.bold: true
                                    }
                                }

                                ThemedSlider {
                                    id: blurSlider
                                    Layout.fillWidth: true
                                    from: 0
                                    to: 100
                                    stepSize: 5
                                }
                            }
                        }

                        SettingsCard {
                            eyebrow: "BATTERY"
                            title: "Power-aware playback"
                            description: "Dial in how aggressively wallpapers should step back when the system is running low."

                            Rectangle {
                                Layout.fillWidth: true
                                radius: 12
                                color: settingsPage.baseColor
                                border.color: settingsPage.borderColor
                                border.width: 1
                                implicitHeight: 72

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 16
                                    spacing: 12

                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        spacing: 4

                                        Label {
                                            text: "Pause video on low battery"
                                            color: "white"
                                            font.pixelSize: 14
                                            font.bold: true
                                        }

                                        Text {
                                            text: "Helps preserve battery life by stopping playback once the threshold is crossed."
                                            color: settingsPage.mutedColor
                                            font.pixelSize: 12
                                            wrapMode: Text.WordWrap
                                            Layout.fillWidth: true
                                        }
                                    }

                                    ThemedSwitch {
                                        id: batterySwitch
                                        Layout.alignment: Qt.AlignVCenter
                                    }
                                }
                            }

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 10
                                enabled: batterySwitch.checked
                                opacity: enabled ? 1 : 0.5

                                RowLayout {
                                    Layout.fillWidth: true

                                    Label {
                                        text: "Battery threshold"
                                        color: "white"
                                        font.pixelSize: 14
                                        font.bold: true
                                    }

                                    Item {
                                        Layout.fillWidth: true
                                    }

                                    Label {
                                        text: Math.round(batterySlider.value) + "%"
                                        color: settingsPage.accentColor
                                        font.pixelSize: 14
                                        font.bold: true
                                    }
                                }

                                ThemedSlider {
                                    id: batterySlider
                                    Layout.fillWidth: true
                                    from: 5
                                    to: 100
                                    stepSize: 5
                                }
                            }
                        }

                        SettingsCard {
                            eyebrow: "SYNC & DISPLAYS"
                            title: "Where settings apply"
                            description: "Keep the lock screen in step and decide whether wallpapers act globally or per screen."

                            Rectangle {
                                Layout.fillWidth: true
                                radius: 12
                                color: settingsPage.baseColor
                                border.color: settingsPage.borderColor
                                border.width: 1
                                implicitHeight: 72

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 16
                                    spacing: 12

                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        spacing: 4

                                        Label {
                                            text: "Sync desktop wallpaper to lock screen"
                                            color: "white"
                                            font.pixelSize: 14
                                            font.bold: true
                                        }

                                        Text {
                                            text: "Reuse the same wallpaper selection and playback configuration for the lock screen."
                                            color: settingsPage.mutedColor
                                            font.pixelSize: 12
                                            wrapMode: Text.WordWrap
                                            Layout.fillWidth: true
                                        }
                                    }

                                    ThemedSwitch {
                                        id: lockSyncSwitch
                                        Layout.alignment: Qt.AlignVCenter
                                    }
                                }
                            }

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 10

                                Label {
                                    text: "Apply wallpaper to"
                                    color: "white"
                                    font.pixelSize: 14
                                    font.bold: true
                                }

                                ThemedComboBox {
                                    id: monitorCombo
                                    Layout.fillWidth: true
                                    textRole: "text"
                                    valueRole: "value"
                                    model: settingsPage.monitorOptions
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
