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
    signal removeClicked()

    MouseArea {
        id: hoverArea
        anchors.fill: parent
        hoverEnabled: true

        onClicked: {
            card.clicked()
            // Ensure focus is dropped from buttons to root if needed
            card.forceActiveFocus()
        }
    }

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

        // Close button at top right
        Rectangle {
            id: closeBtn
            width: 28
            height: 28
            radius: 14
            anchors.top: parent.top
            anchors.right: parent.right
            anchors.margins: 8
            color: closeMouseArea.containsMouse ? "#ff6b6b" : "#B3141519"
            border.color: "#1AFFFFFF"
            border.width: 1
            z: 10
            
            Text {
                anchors.centerIn: parent
                text: "✕"
                color: "white"
                font.pixelSize: 14
                font.bold: true
            }
            
            MouseArea {
                id: closeMouseArea
                anchors.fill: parent
                hoverEnabled: true
                // Prevent click passing to main card hover area
                propagateComposedEvents: false
                onClicked: {
                    card.removeClicked()
                }
            }
        }
    }

}
