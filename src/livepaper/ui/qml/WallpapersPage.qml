import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: wallpapersPage
    
    signal wallpaperSelected(var wallpaperItem)

    // Load dynamic wallpapers from python bridge
    property var wallpaperList: []
    
    // Auto-refresh when signal received
    Connections {
        target: appBridge
        function onWallpapersChanged() {
            wallpapersPage.refresh()
        }
    }
    
    Component.onCompleted: {
        refresh()
    }
    
    function refresh() {
        var items = appBridge.getWallpapers()
        listModel.clear()
        for (var i = 0; i < items.length; i++) {
            listModel.append(items[i])
        }
    }

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

            // Only show + Add Wallpaper here if there are wallpapers
            Button {
                id: addBtnTop
                text: "＋ Add Wallpaper"
                font.pixelSize: 14
                font.bold: true
                visible: listModel.count > 0
                
                contentItem: Text {
                    text: addBtnTop.text
                    font: addBtnTop.font
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                
                background: Rectangle {
                    implicitWidth: 160
                    implicitHeight: 40
                    color: addBtnTop.down ? Qt.darker("#228be6", 1.2) : "#228be6"
                    radius: 8
                }
                
                onClicked: appBridge.openAddDialog()
            }
        }

        // Grid Area (when wallpapers exist)
        GridView {
            id: grid
            Layout.fillWidth: true
            Layout.fillHeight: true
            cellWidth: 260
            cellHeight: 180
            clip: true
            visible: listModel.count > 0

            model: ListModel { id: listModel }

            delegate: WallpaperCard {
                wallpaperName: model.name
                imageSource: model.imageSource
                
                onClicked: {
                    wallpapersPage.wallpaperSelected({
                        "name": model.name,
                        "path": model.path,
                        "imageSource": model.imageSource
                    })
                }
                
                onRemoveClicked: {
                    appBridge.removeWallpaper(model.path)
                    // If the removed wallpaper was selected, clear the selection
                    wallpapersPage.wallpaperSelected(null)
                }
            }
        }
        
        // Empty State (when no wallpapers)
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: listModel.count === 0
            
            ColumnLayout {
                anchors.centerIn: parent
                spacing: 24
                
                Label {
                    text: "No wallpapers yet.\nClick 'Add Wallpaper' to get started."
                    color: "#8A8D98"
                    font.pixelSize: 16
                    horizontalAlignment: Text.AlignHCenter
                    Layout.alignment: Qt.AlignHCenter
                }
                
                Button {
                    id: addBtnCenter
                    text: "＋ Add Wallpaper"
                    font.pixelSize: 16
                    font.bold: true
                    Layout.alignment: Qt.AlignHCenter
                    
                    contentItem: Text {
                        text: addBtnCenter.text
                        font: addBtnCenter.font
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    background: Rectangle {
                        implicitWidth: 180
                        implicitHeight: 48
                        color: addBtnCenter.down ? Qt.darker("#228be6", 1.2) : "#228be6"
                        radius: 8
                    }
                    
                    onClicked: appBridge.openAddDialog()
                }
            }
        }
    }
}
