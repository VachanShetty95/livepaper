import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: actionPanel
    width: 320
    Layout.fillHeight: true
    color: "#0A0A0C"
    
    // Optional left border separator
    Rectangle {
        width: 1
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        color: "#141519"
    }

    property var selectedItem: null
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 24
        visible: selectedItem !== null
        
        Label {
            text: "Inspector"
            font.pixelSize: 18
            color: "white"
            font.bold: true
            Layout.alignment: Qt.AlignLeft
        }

        // Selected Image Preview
        Rectangle {
            Layout.fillWidth: true
            height: 200
            radius: 16
            color: "#141519"
            border.color: "#2A2B30"
            border.width: 1
            clip: true
            
            Image {
                anchors.fill: parent
                source: actionPanel.selectedItem ? actionPanel.selectedItem.imageSource : ""
                fillMode: Image.PreserveAspectCrop
                visible: actionPanel.selectedItem !== null && actionPanel.selectedItem.imageSource !== ""
            }

            // Fallback content
            Label {
                anchors.centerIn: parent
                text: "Preview"
                color: "#8A8D98"
                font.pixelSize: 16
                visible: actionPanel.selectedItem === null || actionPanel.selectedItem.imageSource === ""
            }
        }

        // Metadata
        ColumnLayout {
            spacing: 8
            
            Label {
                text: actionPanel.selectedItem ? actionPanel.selectedItem.name : "Unknown Name"
                font.pixelSize: 16
                color: "white"
                font.bold: true
                wrapMode: Text.Wrap
                Layout.fillWidth: true
            }

            Label {
                text: "Resolution: 3840x2160\nFile Size: 12.4 MB" // Could be dynamic from python
                font.pixelSize: 13
                color: "#8A8D98"
                lineHeight: 1.4
            }
        }

        Item { Layout.fillHeight: true } // spacer pushes buttons down

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
                contentItem: Text {
                    text: desktopBtn.text
                    font: desktopBtn.font
                    color: desktopBtn.down ? "#00FFA3" : "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                background: Rectangle {
                    color: "transparent"
                    border.color: desktopBtn.down ? "#00FFA3" : "#2A2B30"
                    border.width: 1
                    radius: 24
                }
                onClicked: {
                    if (actionPanel.selectedItem) {
                        appBridge.applyWallpaper(actionPanel.selectedItem.path, "desktop")
                    }
                }
            }

            Button {
                id: lockScreenBtn
                Layout.fillWidth: true
                height: 48
                text: "Apply to Lock Screen"
                font.pixelSize: 14
                font.bold: true
                contentItem: Text {
                    text: lockScreenBtn.text
                    font: lockScreenBtn.font
                    color: lockScreenBtn.down ? "#00FFA3" : "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                background: Rectangle {
                    color: "transparent"
                    border.color: lockScreenBtn.down ? "#00FFA3" : "#2A2B30"
                    border.width: 1
                    radius: 24
                }
                onClicked: {
                    if (actionPanel.selectedItem) {
                        appBridge.applyWallpaper(actionPanel.selectedItem.path, "lock_screen")
                    }
                }
            }

            Button {
                id: bothBtn
                Layout.fillWidth: true
                height: 48
                text: "Apply to Both"
                font.pixelSize: 14
                font.bold: true
                
                contentItem: Text {
                    text: bothBtn.text
                    font: bothBtn.font
                    color: "#0A0A0C" // Dark text
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                
                background: Rectangle {
                    color: bothBtn.down ? Qt.darker("#00FFA3", 1.2) : "#00FFA3"
                    radius: 24
                }
                onClicked: {
                    if (actionPanel.selectedItem) {
                        appBridge.applyWallpaper(actionPanel.selectedItem.path, "both")
                    }
                }
            }
        }
    }
    
    // Placeholder when nothing selected
    ColumnLayout {
        anchors.centerIn: parent
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
