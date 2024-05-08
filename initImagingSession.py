from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import os


class newImagingSession(QDialog):
    def __init__(self):
        super().__init__()

        #Information to pass to main program from new imaging session
            #Location of imaging session
            #Number of LEDs setup
            #Which LEDs setup 
            

        self.infoTextArr = [
            'Create an ID name for this imaging session.',
            'Backkground image',
            'Green lightfield',
            'Red lightfield',
            'Blue Lightfield'
        ]

        self.layoutImagingSession = QGridLayout(self)
        #Information display left coloumn
        self.txtInfo = QLabel(self.infoTextArr[0])
        
        #Multi tab onright coloumn
        self.tabImagingSession = QTabWidget()
        self.createImagingSessionTabs()
        self.tabImagingSession.currentChanged.connect(self.updateTabInfo)

        #Cancel bottom left
        self.btnCancel = QPushButton('Cancel')
        self.btnCancel.clicked.connect(self.close)

        #Next Bottom middle
        self.btnNext = QPushButton('Next')
        self.btnNext.clicked.connect(self.nextPushed)

        #Next Bottom middle
        self.btnSkip = QPushButton('Skip')
        self.btnSkip.clicked.connect(self.skipPushed)

        self.layoutImagingSession.addWidget(self.txtInfo,0,0)
        self.layoutImagingSession.addWidget(self.tabImagingSession,0,1)
        self.layoutImagingSession.addWidget(self.btnCancel,1,0)
        self.layoutImagingSession.addWidget(self.btnNext,1,1)


    def createImagingSessionTabs(self):
        #Tab 1: Session ID
        self.sessionIDTab = QWidget()
        self.sessionIDLayout = QGridLayout()
        self.sessionIDTab.setLayout(self.sessionIDLayout)
        self.lblSessionID = QLabel('Session ID: ')
        self.txtboxSessionID = QLineEdit() #Textbox for user input

        self.sessionIDLayout.addWidget(self.lblSessionID,0,0)
        self.sessionIDLayout.addWidget(self.txtboxSessionID,0,1)

        self.tabImagingSession.addTab(self.sessionIDTab,'Step 1')
                
        #Tab 2: BKG
        self.backgroundTab = QWidget()
        self.backgroundTabLayout = QGridLayout()
        self.backgroundTab.setLayout(self.backgroundTabLayout)
        self.btnCaptureBackground = QPushButton('Capture Background')#Btn to begin saving
        self.pbCaptureBackgroundProgress = QProgressBar()#Progress bar
        self.gvCaptureBackground = QGraphicsView() #Live image feed

        self.backgroundTabLayout.addWidget(self.btnCaptureBackground,0,0)
        self.backgroundTabLayout.addWidget(self.pbCaptureBackgroundProgress,0,1)
        self.backgroundTabLayout.addWidget(self.gvCaptureBackground,1,0)

        self.tabImagingSession.addTab(self.backgroundTab,'Step 2')


        #Tab 3: Green LF
        self.greenLFTab = QWidget()
        self.greenLFTabLayout = QGridLayout()
        self.greenLFTab.setLayout(self.greenLFTabLayout)
        self.btnCaptureGreenLF = QPushButton('Capture blue lightfield')#Btn to begin saving
        self.pbCaptureGreenLFProgress = QProgressBar()#Progress bar
        self.gvCaptureGreenLF = QGraphicsView() #Live image feed

        self.greenLFTabLayout.addWidget(self.btnCaptureGreenLF,0,0)
        self.greenLFTabLayout.addWidget(self.pbCaptureGreenLFProgress,0,1)
        self.greenLFTabLayout.addWidget(self.gvCaptureGreenLF,1,0)

        self.tabImagingSession.addTab(self.greenLFTab,'Step 3')

        #Tab 4: Red LF
        self.redLFTab = QWidget()
        self.redLFTabLayout = QGridLayout()
        self.redLFTab.setLayout(self.redLFTabLayout)
        self.btnCaptureRedLF = QPushButton('Capture red lightfield')#Btn to begin saving
        self.pbCaptureRedLFProgress = QProgressBar()#Progress bar
        self.gvCaptureRedLF = QGraphicsView() #Live image feed

        self.redLFTabLayout.addWidget(self.btnCaptureRedLF,0,0)
        self.redLFTabLayout.addWidget(self.pbCaptureRedLFProgress,0,1)
        self.redLFTabLayout.addWidget(self.gvCaptureRedLF,1,0)

        self.tabImagingSession.addTab(self.redLFTab,'Step 4')

        #Tab 5: Blue LF
        self.blueLFTab = QWidget()
        self.blueLFTabLayout = QGridLayout()
        self.blueLFTab.setLayout(self.blueLFTabLayout)
        self.btnCaptureBlueLF = QPushButton('Capture NIR lightfield')#Btn to begin saving
        self.pbCaptureBlueLFProgress = QProgressBar()#Progress bar
        self.gvCaptureBlueLF = QGraphicsView() #Live image feed

        self.blueLFTabLayout.addWidget(self.btnCaptureBlueLF,0,0)
        self.blueLFTabLayout.addWidget(self.pbCaptureBlueLFProgress,0,1)
        self.blueLFTabLayout.addWidget(self.gvCaptureBlueLF,1,0)

        self.tabImagingSession.addTab(self.blueLFTab,'Step 5')
        pass

    def updateTabInfo(self):
        currentTab = self.tabImagingSession.currentIndex()
        self.txtInfo.setText(self.infoTextArr[currentTab])

    def nextPushed(self):
        #get active tab
        currentTab = self.tabImagingSession.currentIndex()
        #if current tab is 0 create session folders
        if currentTab == 0:
            self.createImagingSessionDirectories()
            pass
        #swap to next active tab if not on final tab
        if currentTab < 5:
            self.tabImagingSession.setCurrentIndex(currentTab + 1)
            #triggers currentChanged signal to update info

    def skipPushed(self):
        #get active tab
        currentTab = self.tabImagingSession.currentIndex()
        #swap to next active tab if not on final tab
        if currentTab < 5:
            self.tabImagingSession.setCurrentIndex(currentTab + 1)
            #triggers currentChanged signal to update info

    def createImagingSessionDirectories(self):
        sessionID = self.txtboxSessionID.text()

        _calibrationPath = "C:/Versicolour/Session Data/" + sessionID + "/Calibration Data/"
        _calibPath5ms = f"{_calibrationPath}Exposure_5ms"
        _calibPath15ms = f"{_calibrationPath}Exposure_15ms"
        _calibPath25ms = f"{_calibrationPath}Exposure_25ms"
        _calibPath50ms = f"{_calibrationPath}Exposure_50ms"
        _calibPath100ms = f"{_calibrationPath}Exposure_100ms"
        _calibPath250ms = f"{_calibrationPath}Exposure_250ms"

        if (not os.path.isdir(_calibrationPath)):
            os.makedirs(_calibrationPath)
            os.mkdir(_calibPath5ms)
            os.mkdir(_calibPath15ms)
            os.mkdir(_calibPath25ms)
            os.mkdir(_calibPath50ms)
            os.mkdir(_calibPath100ms)
            os.mkdir(_calibPath250ms)
        pass




if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)    

    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)

    app.setPalette(palette)
    window = newImagingSession()
    window.show()
    sys.exit(app.exec())