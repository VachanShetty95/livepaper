import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: sidebar
    width: 250
    Layout.fillHeight: true
    color: "#0A0A0C"

    property string activeItem: "Home"

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 16

        // Logo/Title
        Item {
            Layout.fillWidth: true
            Layout.bottomMargin: 24

            implicitHeight: 54

            RowLayout {
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 10

                Image {
                    source: "../assets/livepaper_logo_mark.png"
                    Layout.preferredWidth: 34
                    Layout.preferredHeight: 34
                    fillMode: Image.PreserveAspectFit
                    mipmap: true
                }

                Image {
                    source: "../assets/livepaper_wordmark.png"
                    Layout.preferredWidth: 150
                    Layout.preferredHeight: 18
                    fillMode: Image.PreserveAspectFit
                    mipmap: true
                }
            }
        }

        // Navigation Items

        Repeater {
            model: [
                { name: "Home", icon: "🏠" },
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
                        font.pixelSize: 20
                        opacity: navItem.isActive ? 1.0 : (navItem.isHovered ? 0.8 : 0.5)
                        Layout.alignment: Qt.AlignVCenter
                    }

                    Label {
                        text: modelData.name
                        font.pixelSize: 18
                        font.bold: navItem.isActive
                        color: navItem.isActive ? "#00FFA3" : (navItem.isHovered ? "white" : "#8A8D98")
                        Layout.alignment: Qt.AlignVCenter
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
