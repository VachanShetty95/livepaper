import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: sidebar
    width: 250
    Layout.fillHeight: true
    color: "#0A0A0C"

    property string activeItem: "Wallpapers"

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 16

        // Logo/Title
        Label {
            text: "LIVEPAPER"
            font.pixelSize: 20
            font.bold: true
            font.letterSpacing: 2
            color: "white"
            Layout.alignment: Qt.AlignHCenter
            Layout.bottomMargin: 24
        }

        // Navigation Items

        Repeater {
            model: [
                { name: "Wallpapers", icon: "🖼️" },
                { name: "Settings", icon: "⚙️" },
                { name: "About", icon: "ℹ️" }
            ]
            delegate: Rectangle {
                id: navItem
                width: parent.width
                height: 48
                radius: 24
                
                property bool isActive: sidebar.activeItem === modelData.name
                property bool isHovered: mouseArea.containsMouse

                color: isActive ? "#1A00FFA3" : (isHovered ? "#141519" : "transparent")
                
                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 20
                    spacing: 12
                    
                    Text {
                        text: modelData.icon
                        font.pixelSize: 16
                        opacity: navItem.isActive ? 1.0 : (navItem.isHovered ? 0.8 : 0.5)
                    }

                    Label {
                        text: modelData.name
                        font.pixelSize: 15
                        font.bold: navItem.isActive
                        color: navItem.isActive ? "#00FFA3" : (navItem.isHovered ? "white" : "#8A8D98")
                    }
                }

                MouseArea {
                    id: mouseArea
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: sidebar.activeItem = modelData.name
                }
            }
        }

        Item {
            // Spacer
            Layout.fillHeight: true
        }
    }
}
