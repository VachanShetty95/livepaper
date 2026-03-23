import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: card
    width: 240
    height: 160
    radius: 16
    color: "#141519"
    border.color: hoverArea.containsMouse ? "#00FFA3" : "#2A2B30"
    border.width: hoverArea.containsMouse ? 2 : 1
    
    // Smooth transition for scale and border
    Behavior on scale { NumberAnimation { duration: 150; easing.type: Easing.OutQuad } }
    scale: hoverArea.containsMouse ? 1.02 : 1.0
    
    property string imageSource: ""
    property string wallpaperName: "Untitled"
    signal clicked()

    Rectangle {
        anchors.fill: parent
        radius: 16
        clip: true
        color: "transparent"
        
        // Use a placeholder if imageSource is not actually loaded, 
        // normally we would use an Image component here.
        Image {
            id: thumbnail
            anchors.fill: parent
            source: card.imageSource
            fillMode: Image.PreserveAspectCrop
            visible: card.imageSource !== ""
        }
        
        // Fallback for null image
        Rectangle {
            anchors.fill: parent
            color: "#1A1C23"
            visible: card.imageSource === ""
            
            Label {
                anchors.centerIn: parent
                text: card.wallpaperName
                color: "#8A8D98"
                font.pixelSize: 14
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.Wrap
                width: parent.width - 24
            }
        }
    }

    MouseArea {
        id: hoverArea
        anchors.fill: parent
        hoverEnabled: true
        onClicked: card.clicked()
    }
}
