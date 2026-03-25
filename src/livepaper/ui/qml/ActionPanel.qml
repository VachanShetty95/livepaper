import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: actionPanel

    property var selectedItem: null

    width: 360
    Layout.fillHeight: true
    color: "#0A0A0C"

    Rectangle {
        width: 1
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        color: "#141519"
    }

    ScrollView {
        id: inspectorScroll

        anchors.fill: parent
        clip: true
        contentWidth: availableWidth
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

        Item {
            width: inspectorScroll.availableWidth
            implicitHeight: selectedItem !== null ? inspectorContent.implicitHeight + 48 : placeholder.implicitHeight + 96

            ColumnLayout {
                id: inspectorContent

                x: 24
                y: 24
                width: Math.max(0, parent.width - 48)
                implicitHeight: childrenRect.height
                spacing: 24
                visible: selectedItem !== null

                Item {
                    implicitHeight: 24
                }

                Label {
                    text: "Inspector"
                    font.pixelSize: 18
                    color: "white"
                    font.bold: true
                    Layout.alignment: Qt.AlignLeft
                }

                // Overview Card
                Rectangle {
                    Layout.fillWidth: true
                    height: 240
                    radius: 16
                    color: "#141519"
                    border.color: "#2A2B30"
                    border.width: 1
                    clip: true

                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 0

                        Image {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            source: actionPanel.selectedItem ? actionPanel.selectedItem.imageSource : ""
                            fillMode: Image.PreserveAspectCrop
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 70
                            color: "transparent"

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 16
                                spacing: 4

                                Text {
                                    text: actionPanel.selectedItem ? actionPanel.selectedItem.name : ""
                                    font.pixelSize: 16
                                    color: "white"
                                    font.bold: true
                                    elide: Text.ElideRight
                                    Layout.fillWidth: true
                                }

                                Text {
                                    text: "Resolution: 3840x2160 • Size: 12.4 MB"
                                    font.pixelSize: 12
                                    color: "#8A8D98"
                                }

                            }

                        }

                    }

                }

                // Plugin Settings
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 16

                    Label {
                        text: "VIDEO SETTINGS"
                        font.pixelSize: 12
                        font.letterSpacing: 1
                        font.bold: true
                        color: "#8A8D98"
                    }

                    // Positioning
                    RowLayout {
                        Layout.fillWidth: true

                        Label {
                            text: "Positioning"
                            color: "white"
                            Layout.fillWidth: true
                        }

                        ComboBox {
                            model: ["Stretch", "Keep Proportions", "Scaled and Cropped"]
                            currentIndex: appBridge.fillMode
                            onActivated: appBridge.fillMode = currentIndex
                            Layout.preferredWidth: 140

                            background: Rectangle {
                                color: "#141519"
                                border.color: parent.hovered ? "#00FFA3" : "#2A2B30"
                                radius: 8
                            }

                            contentItem: Text {
                                text: parent.currentText
                                color: "white"
                                verticalAlignment: Text.AlignVCenter
                                leftPadding: 12
                            }

                        }

                    }

                    // Background
                    RowLayout {
                        Layout.fillWidth: true
                        enabled: appBridge.fillMode === 1
                        opacity: enabled ? 1 : 0.5

                        Label {
                            text: "Background"
                            color: "white"
                            Layout.fillWidth: true
                        }

                        ComboBox {
                            model: ["Solid", "Blur"]
                            currentIndex: appBridge.fillBlur ? 1 : 0
                            onActivated: appBridge.fillBlur = currentIndex === 1
                            Layout.preferredWidth: 140

                            background: Rectangle {
                                color: "#141519"
                                border.color: parent.hovered ? "#00FFA3" : "#2A2B30"
                                radius: 8
                            }

                            contentItem: Text {
                                text: parent.currentText
                                color: "white"
                                verticalAlignment: Text.AlignVCenter
                                leftPadding: 12
                            }

                        }

                    }

                    // Play in Loop
                    RowLayout {
                        Layout.fillWidth: true

                        Label {
                            text: "Play in Loop"
                            color: "white"
                            Layout.fillWidth: true
                        }

                        Switch {
                            checked: appBridge.loop
                            onCheckedChanged: appBridge.loop = checked

                            indicator: Rectangle {
                                implicitWidth: 44
                                implicitHeight: 24
                                radius: 12
                                color: parent.checked ? "#00FFA3" : "#2A2B30"
                                border.color: parent.checked ? "#00FFA3" : "#8A8D98"

                                Rectangle {
                                    x: parent.checked ? parent.width - width - 2 : 2
                                    y: 2
                                    width: 20
                                    height: 20
                                    radius: 10
                                    color: parent.checked ? "#0A0A0C" : "#8A8D98"

                                    Behavior on x {
                                        NumberAnimation {
                                            duration: 150
                                        }

                                    }

                                }

                            }

                        }

                    }

                    // Audio Mute
                    RowLayout {
                        Layout.fillWidth: true

                        Label {
                            text: "Audio Setup"
                            color: "white"
                            Layout.fillWidth: true
                        }

                        RowLayout {
                            spacing: 8

                            Label {
                                text: "Muted"
                                color: appBridge.muteAudio ? "white" : "#8A8D98"
                                font.pixelSize: 12
                            }

                            Switch {
                                checked: !appBridge.muteAudio
                                onCheckedChanged: appBridge.muteAudio = !checked

                                indicator: Rectangle {
                                    implicitWidth: 44
                                    implicitHeight: 24
                                    radius: 12
                                    color: parent.checked ? "#00FFA3" : "#2A2B30"
                                    border.color: parent.checked ? "#00FFA3" : "#8A8D98"

                                    Rectangle {
                                        x: parent.checked ? parent.width - width - 2 : 2
                                        y: 2
                                        width: 20
                                        height: 20
                                        radius: 10
                                        color: parent.checked ? "#0A0A0C" : "#8A8D98"

                                        Behavior on x {
                                            NumberAnimation {
                                                duration: 150
                                            }

                                        }

                                    }

                                }

                            }

                            Label {
                                text: "Sound"
                                color: !appBridge.muteAudio ? "white" : "#8A8D98"
                                font.pixelSize: 12
                            }

                        }

                    }

                    // Speed
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 8
                        Layout.topMargin: 8

                        RowLayout {
                            Layout.fillWidth: true

                            Label {
                                text: "Playback Speed"
                                color: "white"
                            }

                            Item {
                                Layout.fillWidth: true
                            }

                            Label {
                                text: appBridge.playbackRate.toFixed(1) + "x"
                                color: "#00FFA3"
                                font.bold: true
                            }

                        }

                        Slider {
                            Layout.fillWidth: true
                            from: 0.1
                            to: 4
                            value: appBridge.playbackRate
                            onValueChanged: appBridge.playbackRate = value

                            background: Rectangle {
                                x: parent.leftPadding
                                y: parent.topPadding + parent.availableHeight / 2 - height / 2
                                implicitWidth: 200
                                implicitHeight: 6
                                width: parent.availableWidth
                                height: implicitHeight
                                radius: 3
                                color: "#2A2B30"

                                Rectangle {
                                    width: parent.visualPosition * parent.width
                                    height: parent.height
                                    color: "#00FFA3"
                                    radius: 3
                                }

                            }

                            handle: Rectangle {
                                x: parent.leftPadding + parent.visualPosition * (parent.availableWidth - width)
                                y: parent.topPadding + parent.availableHeight / 2 - height / 2
                                implicitWidth: 20
                                implicitHeight: 20
                                radius: 10
                                color: parent.pressed ? "#33FFB7" : "#00FFA3"
                            }

                        }

                    }

                }

                Item {
                    implicitHeight: 24
                }

                // Action Buttons
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 12

                    Button {
                        id: desktopBtn

                        Layout.fillWidth: true
                        height: 48
                        text: "Apply to Desktop"
                        font.pixelSize: 14
                        font.bold: true
                        onClicked: {
                            if (actionPanel.selectedItem)
                                appBridge.applyWallpaper(actionPanel.selectedItem.path, "desktop");

                        }

                        contentItem: Text {
                            text: desktopBtn.text
                            font: desktopBtn.font
                            color: desktopBtn.hovered ? "#00FFA3" : "white"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }

                        background: Rectangle {
                            color: "transparent"
                            border.color: desktopBtn.hovered ? "#00FFA3" : "#2A2B30"
                            border.width: 1
                            radius: 24
                        }

                    }

                    Button {
                        id: lockScreenBtn

                        Layout.fillWidth: true
                        height: 48
                        text: "Apply to Lock Screen"
                        font.pixelSize: 14
                        font.bold: true
                        onClicked: {
                            if (actionPanel.selectedItem)
                                appBridge.applyWallpaper(actionPanel.selectedItem.path, "lock screen");

                        }

                        contentItem: Text {
                            text: lockScreenBtn.text
                            font: lockScreenBtn.font
                            color: lockScreenBtn.hovered ? "#00FFA3" : "white"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }

                        background: Rectangle {
                            color: "transparent"
                            border.color: lockScreenBtn.hovered ? "#00FFA3" : "#2A2B30"
                            border.width: 1
                            radius: 24
                        }

                    }

                    Button {
                        id: bothBtn

                        Layout.fillWidth: true
                        height: 48
                        text: "Apply to Both"
                        font.pixelSize: 14
                        font.bold: true
                        onClicked: {
                            if (actionPanel.selectedItem)
                                appBridge.applyWallpaper(actionPanel.selectedItem.path, "both");

                        }

                        contentItem: Text {
                            text: bothBtn.text
                            font: bothBtn.font
                            color: "#0A0A0C"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }

                        background: Rectangle {
                            color: bothBtn.hovered ? "#33FFB7" : "#00FFA3"
                            radius: 24
                        }

                    }

                }

            }

            // Placeholder when nothing selected
            ColumnLayout {
                id: placeholder

                width: Math.max(0, parent.width - 48)
                implicitHeight: childrenRect.height
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                spacing: 16
                visible: selectedItem === null

                Label {
                    text: "No Wallpaper Selected"
                    font.pixelSize: 16
                    color: "#8A8D98"
                    Layout.alignment: Qt.AlignHCenter
                }

            }

        }

    }

}
