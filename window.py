import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QGridLayout Example")
        self.setGeometry(50, 50, 1100, 750)


        # Create a QGridLayout instance
        layout = QGridLayout()


        self.displayTabs = QTabWidget()
        self.tabSingleDisplay()
        self.tabMultiDisplay()

        self.group = QGroupBox()
        self.createButtonGroup()

        self.settingsTabs = QTabWidget()
        self.tabContrastSettings()
        

        # Add widgets to the layout
        layout.addWidget(self.displayTabs,0,0,0,5)
        layout.addWidget(self.group,0,5)
        layout.addWidget(self.settingsTabs,1,5,1,2)

        # Set the layout on the application's window
        self.setLayout(layout)


    def tabSingleDisplay(self):
        self.singleDisplay = QWidget()
        self.displayTabs.addTab(self.singleDisplay, "singleDisplay")
        self.openFile = QPushButton("Choose Tab ", self.singleDisplay)
        self.openFile.setGeometry(QRect(700, 25, 200, 30))

    def tabMultiDisplay(self):
        self.multiDisplay = QWidget()
        self.displayTabs.addTab(self.multiDisplay, "multiDisplay")

    def createButtonGroup(self):
        groupLayout = QGridLayout()
        self.group.setLayout(groupLayout)

        groupLayout.addWidget(QPushButton("Button at (0, 0)"), 2, 0)
        groupLayout.addWidget(QPushButton("Button at (0, 1)"), 2, 1)
        groupLayout.addWidget(QPushButton("Button at (0, 2)"), 2, 2)
        groupLayout.addWidget(QPushButton("Button at (1, 0)"), 3, 0)
        groupLayout.addWidget(QPushButton("Button at (1, 1)"), 3, 1)
        groupLayout.addWidget(QPushButton("Button at (1, 2)"), 3, 2)
        groupLayout.addWidget(QPushButton("Button at (2, 0)"), 4, 0)
        groupLayout.addWidget(QPushButton("Button at (2, 1)"), 4, 1)
        groupLayout.addWidget(QPushButton("Button at (2, 2)"), 4, 2)

    def tabContrastSettings(self):
        self.contrastSliders = QWidget()
        self.settingsTabs.addTab(self.contrastSliders, "Contrast")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())