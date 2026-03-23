import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window

ApplicationWindow {
    id: window
    visible: true
    width: 1280
    height: 800
    title: "Livepaper IQON"
    color: "#0A0A0C"

    // Set default application font
    font.family: "Inter"

    RowLayout {
        anchors.fill: parent
        spacing: 0

        Sidebar {
            id: sidebar
            Layout.preferredWidth: 250
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#0A0A0C"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 32
                spacing: 24

                Label {
                    text: sidebar.activeItem
                    font.pixelSize: 28
                    font.bold: true
                    color: "white"
                }

                GridView {
                    id: grid
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    cellWidth: 260
                    cellHeight: 180
                    clip: true

                    model: ListModel {
                        ListElement { name: "Neon City Break" }
                        ListElement { name: "Abstract Dimensions" }
                        ListElement { name: "Cyberpunk 2077" }
                        ListElement { name: "Dark Forest Minimal" }
                        ListElement { name: "Quantum Fluctuations" }
                        ListElement { name: "Deep Space Redux" }
                    }

                    delegate: WallpaperCard {
                        wallpaperName: model.name
                        onClicked: actionPanel.selectedItem = { "name": model.name, "imageSource": "" }
                    }
                }
            }
        }

        ActionPanel {
            id: actionPanel
            Layout.preferredWidth: 300
        }
    }
}
