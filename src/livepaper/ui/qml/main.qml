import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window

ApplicationWindow {
    id: window
    visible: true
    width: 1280
    height: 800
    title: "Livepaper"
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

            StackLayout {
                anchors.fill: parent
                currentIndex: sidebar.activeItem === "Home" ? 0 :
                              sidebar.activeItem === "Wallpapers" ? 1 :
                              sidebar.activeItem === "Settings" ? 2 : 3

                HomePage {
                    onContinueClicked: sidebar.activeItem = "Wallpapers"
                }

                WallpapersPage {
                    onWallpaperSelected: function(item) {
                        actionPanel.selectedItem = item
                    }
                }
                
                SettingsPage {
                }

                AboutPage {
                }
            }
        }

        ActionPanel {
            id: actionPanel
            Layout.preferredWidth: 300
            visible: sidebar.activeItem === "Wallpapers"
        }
    }
}
