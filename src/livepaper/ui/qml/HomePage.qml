import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    color: "#0A0A0C"

    property var systemChecks: []
    property bool allPassed: false

    signal continueClicked()

    Component.onCompleted: {
        // Generate random greeting
        var greetings = ["Welcome", "Welcome Back", "Hello"]
        var greeting = greetings[Math.floor(Math.random() * greetings.length)]
        greetingText.text = greeting + " " + appBridge.username

        // Connect signal
        appBridge.systemCheckCompleted.connect(function(results) {
            systemChecks = results
            var passed = true
            for (var i = 0; i < results.length; i++) {
                if (!results[i].passed) passed = false
            }
            allPassed = passed
        })

        // Run check on load
        appBridge.runSystemCheck()
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 40
        spacing: 32

        // Top Header
        RowLayout {
            Layout.fillWidth: true
            
            Text {
                id: greetingText
                font.pixelSize: 36
                font.bold: true
                color: "white"
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignVCenter
            }

            Button {
                text: "Re-check"
                font.pixelSize: 14
                Layout.alignment: Qt.AlignVCenter
                
                background: Rectangle {
                    implicitWidth: 100
                    implicitHeight: 40
                    color: parent.hovered ? "#141519" : "transparent"
                    border.color: parent.hovered ? "#00FFA3" : "#2A2B30"
                    border.width: 1
                    radius: 20
                }
                contentItem: Text {
                    text: parent.text
                    color: parent.hovered ? "#00FFA3" : "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                
                onClicked: {
                    systemChecks = []  // clear
                    appBridge.runSystemCheck()
                }
            }
        }

        // Center Content (Dependencies)
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 16

            Repeater {
                model: systemChecks
                delegate: Rectangle {
                    Layout.fillWidth: true
                    width: parent.width
                    height: 80
                    color: "#141519"
                    border.color: "#2A2B30"
                    border.width: 1
                    radius: 16

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 16

                        // Status indicator
                        Rectangle {
                            width: 20
                            height: 20
                            radius: 10
                            color: modelData.passed ? "#00FFA3" : "#FF3366"
                            Layout.alignment: Qt.AlignVCenter
                        }

                        // Texts
                        ColumnLayout {
                            spacing: 4
                            Layout.alignment: Qt.AlignVCenter

                            Text {
                                text: modelData.name
                                font.pixelSize: 16
                                font.bold: true
                                color: "white"
                            }
                            Text {
                                text: modelData.passed ? "Installed" : "Not installed"
                                font.pixelSize: 14
                                color: "#8A8D98"
                            }
                        }

                        Item { Layout.fillWidth: true }

                        // Install Button
                        Button {
                            text: "Install"
                            enabled: !modelData.passed
                            Layout.alignment: Qt.AlignVCenter
                            
                            background: Rectangle {
                                implicitWidth: 90
                                implicitHeight: 36
                                radius: 18
                                color: parent.enabled ? (parent.hovered ? "#33FFB7" : "#00FFA3") : "#2A2B30"
                            }
                            contentItem: Text {
                                text: parent.text
                                color: parent.enabled ? "#0A0A0C" : "#8A8D98"
                                font.bold: true
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }

                            onClicked: {
                                if (modelData.fix_url) {
                                    appBridge.openUrl(modelData.fix_url)
                                }
                            }
                        }
                    }
                }
            }
        }

        Item { Layout.fillHeight: true } // spacer

        // Bottom Right
        RowLayout {
            Layout.fillWidth: true
            Item { Layout.fillWidth: true } // spacer
            
            Button {
                text: "Continue →"
                
                background: Rectangle {
                    implicitWidth: 140
                    implicitHeight: 48
                    radius: 24
                    color: parent.hovered ? "#33FFB7" : "#00FFA3"
                }
                contentItem: Text {
                    text: parent.text
                    color: "#0A0A0C"
                    font.bold: true
                    font.pixelSize: 16
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }

                onClicked: {
                    root.continueClicked()
                }
            }
        }
    }
}
