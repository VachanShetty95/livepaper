import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: wallpapersPage
    
    signal wallpaperSelected(var wallpaperItem)

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 32
        spacing: 24

        // Top Toolbar
        RowLayout {
            Layout.fillWidth: true
            
            Label {
                text: "Wallpapers"
                font.pixelSize: 28
                font.bold: true
                color: "white"
                Layout.fillWidth: true
            }

            Button {
                id: addBtnTop
                text: "＋ Add Wallpaper"
                font.pixelSize: 14
                font.bold: true
                
                contentItem: Text {
                    text: addBtnTop.text
                    font: addBtnTop.font
                    color: "#0A0A0C"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                
                background: Rectangle {
                    implicitWidth: 160
                    implicitHeight: 40
                    color: addBtnTop.hovered ? "#33FFB7" : "#00FFA3"
                    radius: 20
                }
                
                onClicked: appBridge.openAddDialog()
            }
        }

        // Grid Area
        GridView {
            id: grid
            Layout.fillWidth: true
            Layout.fillHeight: true
            cellWidth: width / 4
            cellHeight: cellWidth * 0.8
            clip: true

            model: appBridge.wallpaperModel

            delegate: Item {
                width: grid.cellWidth
                height: grid.cellHeight

                Rectangle {
                    anchors.fill: parent
                    anchors.margins: 12
                    color: "#141519"
                    border.color: hoverArea.containsMouse ? "#00FFA3" : "#2A2B30"
                    border.width: 1
                    radius: 16
                    clip: true

                    MouseArea {
                        id: hoverArea
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: {
                            wallpapersPage.wallpaperSelected({
                                "name": model.name,
                                "path": model.path,
                                "imageSource": model.imageSource
                            })
                        }
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 0

                        // Thumbnail
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: "black"
                            
                            Image {
                                anchors.fill: parent
                                source: model.imageSource
                                fillMode: Image.PreserveAspectCrop
                            }
                        }

                        // Remove Button
                        Rectangle {
                            width: 28
                            height: 28
                            radius: 14
                            color: "#0A0A0C"
                            border.color: "#FF3366"
                            opacity: removeHover.containsMouse ? 1.0 : 0.0
                            visible: hoverArea.containsMouse || removeHover.containsMouse
                            anchors.top: parent.top
                            anchors.right: parent.right
                            anchors.topMargin: 8
                            anchors.rightMargin: 8
                            
                            Text {
                                text: "×"
                                anchors.centerIn: parent
                                color: "#FF3366"
                                font.pixelSize: 20
                                font.bold: true
                                verticalAlignment: Text.AlignVCenter
                                horizontalAlignment: Text.AlignHCenter
                                topPadding: -2 // adjustments for text centering
                            }

                            MouseArea {
                                id: removeHover
                                anchors.fill: parent
                                hoverEnabled: true
                                onClicked: {
                                    appBridge.removeWallpaper(model.path)
                                    wallpapersPage.wallpaperSelected(null)
                                }
                            }
                        }

                        // Footer
                        Rectangle {
                            Layout.fillWidth: true
                            height: 48
                            color: "transparent"

                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: 16
                                anchors.rightMargin: 16
                                spacing: 12
                                
                                Rectangle {
                                    width: 8
                                    height: 8
                                    radius: 4
                                    color: "#00FFA3"
                                    Layout.alignment: Qt.AlignVCenter
                                }

                                Text {
                                    text: model.name
                                    color: "white"
                                    font.pixelSize: 14
                                    font.bold: true
                                    elide: Text.ElideRight
                                    Layout.fillWidth: true
                                    Layout.alignment: Qt.AlignVCenter
                                }
                            }
                        }
                    }
                }
            }
        }
        
        // Empty State Handler
        Label {
            visible: grid.count === 0
            text: "No wallpapers yet. Click 'Add Wallpaper' to get started."
            color: "#8A8D98"
            font.pixelSize: 16
            horizontalAlignment: Text.AlignHCenter
            Layout.alignment: Qt.AlignHCenter
        }
    }
}
