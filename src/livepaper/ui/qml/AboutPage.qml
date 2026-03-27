import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: aboutPage

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 24

        Image {
            source: "../assets/livepaper_logo_mark.png"
            Layout.preferredWidth: 120
            Layout.preferredHeight: 96
            fillMode: Image.PreserveAspectFit
            mipmap: true
            Layout.alignment: Qt.AlignHCenter
        }

        Image {
            source: "../assets/livepaper_wordmark.png"
            Layout.preferredWidth: 240
            Layout.preferredHeight: 28
            fillMode: Image.PreserveAspectFit
            mipmap: true
            Layout.alignment: Qt.AlignHCenter
        }

        // Version
        Label {
            text: "Version 1.0.0" // Ideally fetched from Python
            font.pixelSize: 14
            color: "#8A8D98"
            Layout.alignment: Qt.AlignHCenter
        }

        Item { height: 16 } // Spacer

        // Description
        Label {
            text: "A polished video wallpaper manager for KDE Plasma 6.\nBuilt on top of Smart Video Wallpaper Reborn."
            font.pixelSize: 14
            color: "white"
            horizontalAlignment: Text.AlignHCenter
            Layout.alignment: Qt.AlignHCenter
            wrapMode: Text.WordWrap
        }

        Item { height: 16 } // Spacer

        // Credits / License
        ColumnLayout {
            Layout.alignment: Qt.AlignHCenter
            spacing: 8
            
            Label {
                text: "Plugin by Luis Bocanegra\nApp by Vachan Shetty"
                font.pixelSize: 12
                color: "#8A8D98"
                horizontalAlignment: Text.AlignHCenter
                Layout.alignment: Qt.AlignHCenter
            }

            Label {
                text: "Licensed under the MIT License"
                font.pixelSize: 12
                color: "#B38A8D98"
                horizontalAlignment: Text.AlignHCenter
                Layout.alignment: Qt.AlignHCenter
            }
        }

        Item { height: 16 } // Spacer

        // Buttons
        ColumnLayout {
            Layout.alignment: Qt.AlignHCenter
            spacing: 12
            
            Button {
                id: githubBtn
                text: "📂  View on GitHub"
                Layout.preferredWidth: 200
                Layout.preferredHeight: 40
                
                contentItem: Text {
                    text: githubBtn.text
                    font.pixelSize: 13
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                
                background: Rectangle {
                    color: githubBtn.down ? "#23FFFFFF" : "#14FFFFFF"
                    border.color: "#26FFFFFF"
                    border.width: 1
                    radius: 8
                }
                
                onClicked: appBridge.openUrl("https://github.com/VachanShetty95/livepaper")
            }

            Button {
                id: pluginBtn
                text: "🔌  Plugin Repository"
                Layout.preferredWidth: 200
                Layout.preferredHeight: 40
                
                contentItem: Text {
                    text: pluginBtn.text
                    font.pixelSize: 13
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                
                background: Rectangle {
                    color: pluginBtn.down ? "#23FFFFFF" : "#14FFFFFF"
                    border.color: "#26FFFFFF"
                    border.width: 1
                    radius: 8
                }
                
                onClicked: appBridge.openUrl("https://github.com/luisbocanegra/plasma-smart-video-wallpaper-reborn")
            }
        }
    }
}
