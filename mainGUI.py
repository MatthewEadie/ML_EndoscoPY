#Beginning of GUI for python version of versi player


from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import os

from mainPipeline import mainPipeline


import numpy as np



class WidgetGallery(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(50, 50, 1100, 750)
        self.setWindowTitle("Styles")


        self.selectedExposure = 25
        self.selectedDataset= ''
        self.datasetFilepath = ''


        # create tool bar
        self.createMenuBar()

        self.mainWindow = Window()
        self.setCentralWidget(self.mainWindow)

        #On init ask user to select ML model
        openML = QMessageBox.question(self, "Open ML model", "Would you like to load an ML model. \n\nWarning not having an ML model loaded will disable some features. An ML model can be loaded later using file > open ML model.", QMessageBox.Yes | QMessageBox.No)

        if openML == QMessageBox.Yes:
            try:
                #Uninit camera if still initalised
                self.openMachineLearningModel()
            except:
                pass


    def createMenuBar(self):
        self.mainMenuBar = QMenuBar()

        self.fileMenu = QMenu("File", self)

        self.mlModelAction = QAction("Select ML model")
        self.mlModelAction.triggered.connect(self.openMachineLearningModel)

        self.mlDatasetAction = QAction("Select Dataset folder")
        self.mlDatasetAction.triggered.connect(self.openMLDataset)

        self.saveImagesAction = QAction("Save images")
        # self.mlDatasetAction.triggered.connect(self.saveImages)

        closeAction = QAction('Exit', self)  
        closeAction.triggered.connect(self.close) 


        self.fileMenu.addAction(self.mlModelAction)
        self.fileMenu.addAction(self.mlDatasetAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.saveImagesAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(closeAction)



        helpMenu = QMenu("Help", self)
        helpMenu.addAction(QAction("&About",self))


        self.mainMenuBar.addMenu(self.fileMenu)
        self.mainMenuBar.addMenu(helpMenu)

        self.setMenuBar(self.mainMenuBar) 

    def openMachineLearningModel(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dialog.setViewMode(QFileDialog.ViewMode.List)
        self.modelDirectoryPath = dialog.getExistingDirectory()


        if self.modelDirectoryPath == "":
            QMessageBox.critical(self, "Missing folder path", "No folder path selected.")
            return

        self.mainWindow.newMLModelOpened(self.modelDirectoryPath)

    def openMLDataset(self):

        #CHANGE TO FILE SELECTION NOT FOLDER
        #SELECTION NEEDS TO BE A 4D .npy STACK

        # self.dataset_filepath = QFileDialog.getOpenFileName(self, "Open File", "./", "Numpy array (*.npy)")[0]

        dialog = QFileDialog(self, "Open dataset")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dialog.setViewMode(QFileDialog.ViewMode.List)
        self.datasetDirectoryPath = dialog.getExistingDirectory()


        if self.datasetDirectoryPath == "":
            QMessageBox.critical(self, "Missing folder path", "No folder path selected.")
            return
        
        self.mainWindow.newMLDatasetDirectory(self.datasetDirectoryPath)
    
    def closeEvent(self, event):
        # Ask for confirmation before closing
        confirmation = QMessageBox.question(self, "Confirmation", "Are you sure you want to close the application?", QMessageBox.Yes | QMessageBox.No)

        if confirmation == QMessageBox.Yes:
            try:
                #Uninit camera if still initalised
                self.mainWindow.mainPipeline.stopAcquisition()
            except:
                pass
            event.accept()  # Close the app
        else:
            event.ignore()  # Don't close the app




























class Window(QWidget):
    beginPlayback = pyqtSignal()
    beginAcquisition = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("QGridLayout Example")


        #----- GLOBAL VARIABLES -----


        self.sessionDirectory = ""

        self.playTF = True #Initalise play stop button as true

        self.recordTF = False #Initialise recording as false

        self.displayMode = 1 # 1 = ML playback, 2 = acquisition

        self.acquisitionSaveLocation = '' #Initalise as empty for use later

        # ---- THREAD INSTANCES ---- #
        # ML THREAD #
        #Create instance of ML pipeline
        self.mainPipeline = mainPipeline()
        #Create QThread to store pipeline
        self.mainThread = QThread()
        self.mainPipeline.moveToThread(self.mainThread)
        #Start the thread as ML playback is default
        self.mainThread.start()
        #Create the ML thread
        self.mainPipeline.createMLThread()

        

        

        #SIGNALS
        self.beginPlayback.connect(self.mainPipeline.runPlayback)
        self.beginAcquisition.connect(self.mainPipeline.runAcquisition)
        

        #SLOTS
        self.mainPipeline.updateImagePlayback.connect(self.updateDisplayPlayback)
        self.mainPipeline.updateImageAcquisition.connect(self.updateDisplayCamera)
        #----------------------------



        # ---- GUI SET UP ---- #
        
        # Create a QGridLayout instance
        layout = QGridLayout()

        #Create software function mode (ML playback or Acquisition)
        self.createSoftwareFunctionMode()
        layout.addWidget(self.modeSelectionGroup,0,0)

        #Create buton for controlling ML application
        self.createmachineLearningToggle()
        layout.addWidget(self.toggleMLGroup,0,1)

        #Create toggle for demo mode
        self.createDemoToggle()
        layout.addWidget(self.toggleDemoGroup, 0,2)


        #Create display image
        self.createDisplayImage()
        layout.addWidget(self.singleDisplay,1,0,5,5)


        #Create list to display datrasets in folder
        self.createDatasetList()
        layout.addWidget(self.grpSessionSettings,1,5)



        #----- SETTINGS TABS -----
        self.settingsTabs = QTabWidget()

        self.createContrastTab()
        self.settingsTabs.addTab(self.contrastTab, "Contrast")

        self.createMachineLearningTab()
        self.settingsTabs.addTab(self.machineLearningTab, "ML settings")

        self.createCameraTab()
        self.settingsTabs.addTab(self.cameraSettingsTab, "Camera Settings")

        


        # Play/pause button
        self.createButtonControls()


        # Add widgets to the layout
        layout.addWidget(self.grpSessionSettings,1,5,1,2)
        layout.addWidget(self.settingsTabs, 2,5,1,2)
        layout.addWidget(self.buttonControlGroup, 6,5)



        #Image selector slider
        self.createImageSlider()
        layout.addWidget(self.groupImageSlider, 6, 0, 1, 5)


        # LABEL FOR USING INFORMATION
        self.txtInfo = QLineEdit('info text')
        self.txtInfo.setReadOnly(True)
        layout.addWidget(self.txtInfo,9,0,1,0)

        self.txtFPS = QLabel('fps counter')
        self.txtFPS.setAlignment(Qt.AlignRight)
        layout.addWidget(self.txtFPS,9,4)





        #SET DEFAULT VALUES AT END OF WIDGET ALLOCATIONS
        #----------------------------------------------
        self.radioExposure25.setChecked(True) #Program default exposure setting is 25ms


        #----------------------------------------------

        # Set the layout on the application's window
        self.setLayout(layout)






    def createSoftwareFunctionMode(self):
        #Horizontal grid box for mode selection
        self.modeSelectionGroup = QGroupBox()
        self.modeSelectionGroupLayout = QHBoxLayout()
        self.modeSelectionGroup.setLayout(self.modeSelectionGroupLayout)

        #Radio buttons for each mode
        self.modeButtonGroup = QButtonGroup()
        self.radioMLMode = QRadioButton('Machine Learning')
        self.radioMLMode.setChecked(True)
        self.radioAcquisitionMode = QRadioButton('Acquisition')

        #Add buttons to group so radio function works correctly
        self.modeButtonGroup.addButton(self.radioMLMode,1)
        self.modeButtonGroup.addButton(self.radioAcquisitionMode,2)

        #Add buttons into mode selection layout to display buttons
        self.modeSelectionGroupLayout.addWidget(self.radioMLMode)
        self.modeSelectionGroupLayout.addWidget(self.radioAcquisitionMode)

        #Only one button needs to be connected when using toggled
        self.radioMLMode.toggled.connect(self.changeDisplayMode)
        # self.radioAcquisitionMode.toggled.connect(self.changeDisplayMode)

    def createmachineLearningToggle(self):
        # ---- Toggle ML operation ---- #
        self.toggleMLGroup = QGroupBox()
        self.toggleMLGroupLayout = QHBoxLayout()
        self.toggleMLGroup.setLayout(self.toggleMLGroupLayout)
        #Button to turn ML on off
        self.btnEnableML = QPushButton('ML on')
        self.btnEnableML.clicked.connect(self.handleToggleML)
        self.toggleMLGroupLayout.addWidget(self.btnEnableML)

        #Disabled on start until ML model is loaded
        self.btnEnableML.setEnabled(False)

        #Set variable to handle toggle ML, True by default
        self.TFmachineLearning = False
        pass

    def createDemoToggle(self):
        # ---- Toggle ML operation ---- #
        self.toggleDemoGroup = QGroupBox()
        self.toggleDemoGroupLayout = QHBoxLayout()
        self.toggleDemoGroup.setLayout(self.toggleDemoGroupLayout)
        #Button to turn ML on off
        self.ckbToggleDemo = QCheckBox('Demo mode')
        self.ckbToggleDemo.clicked.connect(self.handleToggleDemo)
        self.toggleDemoGroupLayout.addWidget(self.ckbToggleDemo)

        #Disabled till camera in initalised
        self.ckbToggleDemo.setEnabled(False)


        #Set variable to handle toggle ML, True by default
        self.TFmachineLearning = False
        pass
        


    def createDisplayImage(self):
        #Layout to contain image display
        self.singleDisplay = QWidget()
        singleDisplayLayout = QGridLayout()
        self.singleDisplay.setLayout(singleDisplayLayout)

        #A scene is required to display images
        self.imageSingleScene = QGraphicsScene()

        #Black pixmap for initial display
        self.displayImage = np.zeros((720,1080))
        height, width = self.displayImage.shape
        bytesPerLine = 3*width
        self.displayImage = QImage(self.displayImage.data, width, height, bytesPerLine, QImage.Format_Grayscale8)
        self.displayImage = QPixmap.fromImage(self.displayImage)
        self.imageSingleScene.addPixmap(self.displayImage)

        #Graphics view widget to display image
        self.imageSingleDisplay = QGraphicsView()
        self.imageSingleDisplay.setScene(self.imageSingleScene)

        #Add graphics view to layout
        singleDisplayLayout.addWidget(self.imageSingleDisplay,0,0)

    def createDatasetList(self):
        #Group layout for dataset list
        self.grpSessionSettings = QGroupBox()
        groupLayout = QGridLayout()
        self.grpSessionSettings.setLayout(groupLayout)

        #List widget for datasets in selected folder
        self.lstDatasetList = QListWidget()
        self.btnSelectDataset = QPushButton("Load dataset")
        self.btnSelectDataset.clicked.connect(self.openNewDataset)

        #Add dataset list widget to layout
        groupLayout.addWidget(self.lstDatasetList, 0, 2, 2, 2)
        groupLayout.addWidget(self.btnSelectDataset, 3, 2)

    def changeDisplayMode(self):
        self.displayMode = self.modeButtonGroup.checkedId()
        try:
            if self.displayMode == 1:
                #End camera thread when swapping to playback
                self.mainPipeline.stopCameraThread()

                #Update controls
                self.changeControlsPlayback()

                #Clear display on switch mode
                self.clearDisplay()

                #Display okay message
                self.okayInfoText('Changed to machine learning mode')

            elif self.displayMode == 2:
                #Create thread for camera acquisition
                self.mainPipeline.createCameraThread() 

                #Update controls for acquisition mode
                self.changeControlsAcquisition()

                #Clear display on switch mode
                self.clearDisplay()

                #Display okay message
                self.okayInfoText('Changed to acquisition mode')

        except:
            self.errorInfoText('Error setting display mode')

    def changeControlsPlayback(self):
        #Remove capture and save buttons
        self.buttonControlGroupLayout.removeWidget(self.btnCapture)
        self.buttonControlGroupLayout.removeWidget(self.btnRecord)
        self.buttonControlGroupLayout.removeWidget(self.btnSave100)
        self.btnCapture.setParent(None)
        self.btnRecord.setParent(None)
        self.btnSave100.setParent(None)

        #Disable Initalise camera button
        self.btnInitaliseCamera.setEnabled(False)

        #Add play/pause button
        self.buttonControlGroupLayout.addWidget(self.btnPlayPause)

        #Enable select dataset button
        self.btnSelectDataset.setEnabled(True)

        #Enable image slider
        self.btnBackImageSlider.setEnabled(True)
        self.imageSlider.setEnabled(True)
        self.btnForwardImageSlider.setEnabled(True)

        pass

    def changeControlsAcquisition(self):

        #Remove play/pause button
        self.buttonControlGroupLayout.removeWidget(self.btnPlayPause)
        self.btnPlayPause.setParent(None)

        #Add capture and save button
        self.buttonControlGroupLayout.addWidget(self.btnCapture,0,0)
        self.buttonControlGroupLayout.addWidget(self.btnRecord,1,0)
        self.buttonControlGroupLayout.addWidget(self.btnSave100,1,1)

        #Disable buttons until camera is initalised and save stack created
        self.btnCapture.setEnabled(False)
        self.btnSave100.setEnabled(False)

        #Enable initalise camera button
        self.btnInitaliseCamera.setEnabled(True)

        #Disable load dataset button
        self.btnSelectDataset.setEnabled(False)

        #Disable image selector
        self.btnBackImageSlider.setEnabled(False)
        self.imageSlider.setEnabled(False)
        self.btnForwardImageSlider.setEnabled(False)
        pass

    def clearDisplay(self):
        #Black pixmap
        self.displayImage = np.zeros((720,1080))
        height, width = self.displayImage.shape
        bytesPerLine = 3*width
        self.displayImage = QImage(self.displayImage.data, width, height, bytesPerLine, QImage.Format_Grayscale8)
        self.displayImage = QPixmap.fromImage(self.displayImage)
        self.imageSingleScene.addPixmap(self.displayImage)

        #Set graphics view to display blank image
        self.imageSingleDisplay.setScene(self.imageSingleScene)
        pass


    def createContrastTab(self):
        #Layout for tab
        self.contrastTab = QWidget()
        self.contrastTabLayout = QVBoxLayout()
        self.contrastTab.setLayout(self.contrastTabLayout)

        #Layout for contrast sliders
        self.grpContrastSliders = QGroupBox()
        self.grpContrastSlidersLayout = QHBoxLayout()
        self.grpContrastSliders.setLayout(self.grpContrastSlidersLayout)

        #Create two sliders (min/max value)
        self.sliderContrastMin = QSlider()
        self.sliderContrastMin.setMaximum(255)
        self.sliderContrastMin.setMinimum(0)
        self.sliderContrastMin.setValue(0)
        self.sliderContrastMax = QSlider()
        self.sliderContrastMax.setMaximum(255)
        self.sliderContrastMax.setMinimum(0)
        self.sliderContrastMax.setValue(255)

        #Update contrast values if sliders changed
        self.sliderContrastMin.sliderMoved.connect(self.updateContrastSettings)
        self.sliderContrastMax.sliderMoved.connect(self.updateContrastSettings)

        #Create label to display value of slider
        self.contrastLabelFont = QFont('Arial', 15)
        self.contrastLabelFont.setBold(True)
        self.lblContrastMin = QLabel('0')
        self.lblContrastMin.setFont(self.contrastLabelFont)
        self.lblContrastMax = QLabel('255')
        self.lblContrastMax.setFont(self.contrastLabelFont)

        #Add slider and labels to slider group
        self.grpContrastSlidersLayout.addWidget(self.lblContrastMin)
        self.grpContrastSlidersLayout.addWidget(self.sliderContrastMin)
        self.grpContrastSlidersLayout.addWidget(self.sliderContrastMax)
        self.grpContrastSlidersLayout.addWidget(self.lblContrastMax)
        
        #Create check box for auto contrast
        self.checkAutoContrast = QCheckBox('Auto contrast')

        #Add sliders and auto contrast toggle to main group
        self.contrastTabLayout.addWidget(self.grpContrastSliders)
        self.contrastTabLayout.addWidget(self.checkAutoContrast)

    def createMachineLearningTab(self):
        self.machineLearningTab = QWidget()
        self.machineLearningTabLayout = QVBoxLayout()
        self.machineLearningTab.setLayout(self.machineLearningTabLayout)

        # ---- Selected Model ---- #
        #Text box for ML directory
        self.lblChosenModel = QLabel('ML Model:')
        self.txtChosenModel = QLineEdit('')
        self.txtChosenModel.setReadOnly(True)

        #Add label and txtbox to tab layout
        self.machineLearningTabLayout.addWidget(self.lblChosenModel)
        self.machineLearningTabLayout.addWidget(self.txtChosenModel)

        # ---- Model input shape ---- #
        #Text box for Dataset directory
        self.lblModelInputShape = QLabel('Model input shape:')
        self.txtModelInputShape = QLineEdit('')
        self.txtModelInputShape.setReadOnly(True)

        #Add label and txtbox to tab layout
        self.machineLearningTabLayout.addWidget(self.lblModelInputShape)
        self.machineLearningTabLayout.addWidget(self.txtModelInputShape)

        # ---- Chosen Dataset ---- #
        #Text box for Dataset directory
        self.lblChosenDataset = QLabel('Selected Dataset:')
        self.txtChosenDataset = QLineEdit('')
        self.txtChosenDataset.setReadOnly(True)

        #Add label and txtbox to tab layout
        self.machineLearningTabLayout.addWidget(self.lblChosenDataset)
        self.machineLearningTabLayout.addWidget(self.txtChosenDataset)

        # ---- Dataset shape ---- #
        #Text box for Dataset directory
        self.lblDatasetShape = QLabel('Dataset shape:')
        self.txtDatasetShape = QLineEdit('')
        self.txtDatasetShape.setReadOnly(True)

        #Add label and txtbox to tab layout
        self.machineLearningTabLayout.addWidget(self.lblDatasetShape)
        self.machineLearningTabLayout.addWidget(self.txtDatasetShape)
        pass

    def createCameraTab(self):
        #Layout for entire camera settings tab
        self.cameraSettingsTab = QWidget()
        self.cameraSettingsLayout = QVBoxLayout()
        self.cameraSettingsTab.setLayout(self.cameraSettingsLayout)

        # ----  CAMERA FUNCTION ---- #
        self.cameraInitGroup = QGroupBox()
        self.cameraInitGroupLayout = QHBoxLayout()
        self.cameraInitGroup.setLayout(self.cameraInitGroupLayout)
        #Initalise camera button
        self.btnInitaliseCamera = QPushButton('Initalise')
        self.btnInitaliseCamera.setEnabled(False) #Defaulty disabled until swapped to acquisition mode
        #Add button to camera init group
        self.cameraInitGroupLayout.addWidget(self.btnInitaliseCamera)
        #Connect button to initalise camera function
        self.btnInitaliseCamera.clicked.connect(self.initaliseCamera)

        #De-Initalise camera button
        self.btnDeInitaliseCamera = QPushButton('De-Initalise')
        self.btnDeInitaliseCamera.setEnabled(False) #Defaulty disabled until swapped to acquisition mode
        #Add button to camera init group
        self.cameraInitGroupLayout.addWidget(self.btnDeInitaliseCamera)
        #Connect button to initalise camera function
        self.btnDeInitaliseCamera.clicked.connect(self.deInitaliseCamera)
        #Add group to camera tab layout
        self.cameraSettingsLayout.addWidget(self.cameraInitGroup)





        # ---- CAMERA INFORMATION ---- #
        #Layout for camera information
        self.grpCameraInfo = QGroupBox('Camera Info')
        self.cameraInfoLayout = QVBoxLayout()
        self.grpCameraInfo.setLayout(self.cameraInfoLayout)

        #Line edit for serial number
        self.lblCameraSN = QLabel('Camera sn')
        self.txtCameraSN = QLineEdit()
        self.txtCameraSN.setReadOnly(True)

        self.cameraInfoLayout.addWidget(self.lblCameraSN)
        self.cameraInfoLayout.addWidget(self.txtCameraSN)

        #Line edit to display camera name
        self.lblCameraName = QLabel('Camera name')
        self.txtCameraName = QLineEdit()
        self.txtCameraName.setReadOnly(True)

        self.cameraInfoLayout.addWidget(self.lblCameraName)
        self.cameraInfoLayout.addWidget(self.txtCameraName)

        #Add group to tab layout
        self.cameraSettingsLayout.addWidget(self.grpCameraInfo)

        # ---- Camera frame size ---- #
        self.grpCameraFrame = QGroupBox('Frame size')
        self.cameraFrameLayout = QGridLayout()
        self.grpCameraFrame.setLayout(self.cameraFrameLayout)

        #Labels to tell user what dimension they're changing
        #Spin box to allow user to enter new dimension
        self.lblFrameX = QLabel('X:')
        self.numFrameX = QSpinBox()
        self.numFrameX.setMinimum(0)
        self.numFrameX.setMaximum(2048)

        self.lblFrameY = QLabel('Y:')
        self.numFrameY = QSpinBox()
        self.numFrameY.setMinimum(0)
        self.numFrameY.setMaximum(2048)

        self.lblFrameXOffset = QLabel('X Offset:')
        self.numFrameXOffset = QSpinBox()
        self.numFrameXOffset.setMinimum(0)
        self.numFrameXOffset.setMaximum(2048)

        self.lblFrameYOffset = QLabel('Y Offset:')
        self.numFrameYOffset = QSpinBox()
        self.numFrameYOffset.setMinimum(0)
        self.numFrameYOffset.setMaximum(2048)

        #Add labels and line edits to layout
        self.cameraFrameLayout.addWidget(self.lblFrameX,0,0)
        self.cameraFrameLayout.addWidget(self.numFrameX,0,1)
        self.cameraFrameLayout.addWidget(self.lblFrameY,0,2)
        self.cameraFrameLayout.addWidget(self.numFrameY,0,3)

        self.cameraFrameLayout.addWidget(self.lblFrameXOffset,1,0)
        self.cameraFrameLayout.addWidget(self.numFrameXOffset,1,1)
        self.cameraFrameLayout.addWidget(self.lblFrameYOffset,1,2)
        self.cameraFrameLayout.addWidget(self.numFrameYOffset,1,3)

        #Group to contain current frame settings
        self.grpCameraCurrentFrame = QGroupBox('Current frame size')
        self.cameraCurrentFrameLayout = QGridLayout()
        self.grpCameraCurrentFrame.setLayout(self.cameraCurrentFrameLayout)

        self.lblCurrentFrameX = QLabel(f'X: ')
        self.lblCurrentFrameY = QLabel(f'Y: ')
        self.lblCurrentFrameXOffset = QLabel(f'X Offset: ')
        self.lblCurrentFrameYOffset = QLabel(f'Y Offset: ')

        self.cameraCurrentFrameLayout.addWidget(self.lblCurrentFrameX,0,0)
        self.cameraCurrentFrameLayout.addWidget(self.lblCurrentFrameY,0,2)
        self.cameraCurrentFrameLayout.addWidget(self.lblCurrentFrameXOffset,1,0)
        self.cameraCurrentFrameLayout.addWidget(self.lblCurrentFrameYOffset,1,2)

        self.cameraFrameLayout.addWidget(self.grpCameraCurrentFrame, 2,0,1,4)

        #Button to set the camera frame to new size enetered above
        self.btnSetCameraFrame = QPushButton('Set frame')
        self.cameraFrameLayout.addWidget(self.btnSetCameraFrame,4,0,1,4)

        #Connect button to function
        self.btnSetCameraFrame.clicked.connect(self.setCameraFrameSize)

        self.cameraSettingsLayout.addWidget(self.grpCameraFrame)



        # ---- EXPOSURE SETTINGS ---- #
        #Layout for exposure settings
        groupExposureSettings = QGroupBox('Exposure time (ms)')
        groupExposureSetLayout = QGridLayout()
        groupExposureSettings.setLayout(groupExposureSetLayout)

        #Button group and radio buttons for exposure presets
        self.btngrpExposure = QButtonGroup()
        self.radioExposure5 = QRadioButton('5')
        self.radioExposure15 = QRadioButton('15')
        self.radioExposure25 = QRadioButton('25')
        self.radioExposure50 = QRadioButton('50')

        #Add buttons to group to work properly
        self.btngrpExposure.addButton(self.radioExposure5,5)
        self.btngrpExposure.addButton(self.radioExposure15,15)
        self.btngrpExposure.addButton(self.radioExposure25,25)
        self.btngrpExposure.addButton(self.radioExposure50,50)

        #Add buttons to layout
        groupExposureSetLayout.addWidget(self.radioExposure5,0,0)
        groupExposureSetLayout.addWidget(self.radioExposure15,0,1)
        groupExposureSetLayout.addWidget(self.radioExposure25,1,0)
        groupExposureSetLayout.addWidget(self.radioExposure50,1,1)

        #Connect radio buttons to functions
        # self.radioExposure5.toggled.connect(self.createTriggerTask)
        # self.radioExposure15.toggled.connect(self.createTriggerTask)
        # self.radioExposure25.toggled.connect(self.createTriggerTask)
        # self.radioExposure50.toggled.connect(self.createTriggerTask)

        #Add exposure settings group to tab layout
        self.cameraSettingsLayout.addWidget(groupExposureSettings)



        # ---- Image save location ---- # 
        #Layout for save location changing
        self.grpSaveLocation = QGroupBox('Save location')
        self.saveLocationLayout = QVBoxLayout()
        self.grpSaveLocation.setLayout(self.saveLocationLayout)

        self.btnChangeSaveLocation = QPushButton('Set save location')
        self.btnChangeSaveLocation.clicked.connect(self.changeSaveLocation)
        self.saveLocationLayout.addWidget(self.btnChangeSaveLocation)

        self.txtSaveLocation = QLineEdit()
        self.txtSaveLocation.setReadOnly(True)
        self.saveLocationLayout.addWidget(self.txtSaveLocation)

        #Add group to layout
        self.cameraSettingsLayout.addWidget(self.grpSaveLocation)

    def createImageSlider(self):
        #h box
        self.groupImageSlider = QWidget()
        self.groupImageSliderLayout = QHBoxLayout()
        self.groupImageSlider.setLayout(self.groupImageSliderLayout)

        #button back image
        self.btnBackImageSlider = QPushButton('<')
        self.btnBackImageSlider.clicked.connect(self.btnBackPressed)

        #slider
        self.imageSlider = QSlider(orientation=Qt.Horizontal)
        self.imageSlider.setMinimum(0)
        self.imageSlider.setMaximum(4000)
        self.imageSlider.sliderMoved.connect(self.sliderMoved)

        #button forward image
        self.btnForwardImageSlider = QPushButton('>')
        self.btnForwardImageSlider.clicked.connect(self.btnForwardPressed)

        #Label for current image number
        self.currentImageNo = 0
        self.maxImage = 0
        self.txtRangeIndicator = QLabel(f'{self.currentImageNo}/{self.maxImage}')

        #Add all components into slider group
        self.groupImageSliderLayout.addWidget(self.btnBackImageSlider)
        self.groupImageSliderLayout.addWidget(self.imageSlider)
        self.groupImageSliderLayout.addWidget(self.btnForwardImageSlider)
        self.groupImageSliderLayout.addWidget(self.txtRangeIndicator)
        pass

    def createButtonControls(self):
        self.buttonControlGroup = QGroupBox()
        self.buttonControlGroupLayout = QGridLayout()
        self.buttonControlGroup.setLayout(self.buttonControlGroupLayout)

        #Push button to control playback
        self.btnPlayPause = QPushButton('Play')
        self.btnPlayPause.clicked.connect(self.handlePlayPause)

        #Add button to layout as playback is default
        self.buttonControlGroupLayout.addWidget(self.btnPlayPause,0,0)

        #CREATE BUTTONS FOR ACQUISITION BUT DON'T ADD THEM
        #Button to tell camera to start capturing
        self.btnCapture = QPushButton('Capture')
        self.btnCapture.clicked.connect(self.handleAcquisition)

        #Button to start recording
        self.btnRecord = QPushButton('Start recording')
        self.btnRecord.setEnabled(False)
        self.btnRecord.clicked.connect(self.toggleRecording)

        #Button to save the last 100 images
        self.btnSave100 = QPushButton('Save 100')
        self.btnSave100.setEnabled(False)
        self.btnSave100.clicked.connect(self.handleSaveImages)


        

    def newSessionOpened(self, directoryPath):
        #Obtain path to selected dataset folder
        self.sessionDirectory = directoryPath
        self.sessionImagingPath = f'{self.sessionDirectory}/'

        #Create list of all items in that folder
        datasetFolders = os.listdir(self.sessionImagingPath)

        self.lstDatasetList.clear() # remove previous entries
        self.lstDatasetList.addItems(datasetFolders)

        tfNewSession = self.playbackPipeline.newSession(folderPath=self.sessionDirectory)
        if tfNewSession:
            self.txtInfo.setText('New session opened.')
        else:
            self.txtInfo.setText('Error opening new session.')

    def newMLModelOpened(self, MLDirectoryPath):
        try:
            #Load model in ML pipeline
            self.mainPipeline.loadMLModel(MLDirectoryPath)

            #Get shape of first layer
            self.firstLayerShape = self.mainPipeline.firstLayerShape
            print(self.firstLayerShape)

            #Update info box and ML tab
            self.okayInfoText('ML model loaded')
            self.txtChosenModel.setText(MLDirectoryPath)
            self.txtModelInputShape.setText(f'{self.firstLayerShape}')

            #Enable ML toggle button
            self.btnEnableML.setEnabled(True)

            #Enable recording, stack based on ML shape
            self.btnRecord.setEnabled(True)
        except:
            #Display error message in info box
            self.errorInfoText('Error loading ML model')
        pass

    def newMLDatasetDirectory(self, MLDatasetPath):
        self.datasetPath = MLDatasetPath
        self.datasets = []
        #Loop over all files in folder
        for file in os.listdir(self.datasetPath):
            #Check file ends with .npy
            if file.endswith(".npy"):
                #Add file to array
                self.datasets.append(file)

        #Remove previous entries
        self.lstDatasetList.clear() 
        #Populate list with files
        self.lstDatasetList.addItems(self.datasets)
        
    def openNewDataset(self):
        try:
            #Get selected item from dataset list
            selectedDataset = self.lstDatasetList.currentItem().text()

            #Load dataset in ML pipeline
            self.datasetShape = self.mainPipeline.loadDataset(f'{self.datasetPath}/{selectedDataset}')

            #Display chosen dataset
            self.txtChosenDataset.setText(f'{self.datasetPath}/{selectedDataset}')

            #Display shape of dataset
            self.txtDatasetShape.setText(f'{self.datasetShape}')
            self.numberOfImages = self.datasetShape[0]-1

            #Configure image selector to fit dataset
            self.configureImageSelector()

            #Check if dataset shape and ML input shape match
            imageShape = self.datasetShape[1:4] #Ignore number of images
            inputModelShape = self.firstLayerShape[1:4] #Ignore first number
            if imageShape == inputModelShape:
                pass
            else:
                #If they don't match display error
                self.errorInfoText(f"Loaded dataset does not match model input shape")
                #Disable play/pause to avoid break
                self.btnPlayPause.setEnabled(False)
                return

            #Display okay message in info box
            self.okayInfoText(f'Dataset loaded: {selectedDataset}')

            #Enable play/pause if disabled previously
            self.btnPlayPause.setEnabled(True)
        except:
            #Disable play/pause to avoid break
            self.btnPlayPause.setEnabled(False)

            #Display error message in info box
            self.errorInfoText('Error loading data')
        pass

    def changeSaveLocation(self):
        #Create fil dialog box to allow user to set folder path
        dialog = QFileDialog(self, "Open dataset")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dialog.setViewMode(QFileDialog.ViewMode.List)
        self.acquisitionSaveLocation = dialog.getExistingDirectory()

        #Check is selected directory exists
        if self.acquisitionSaveLocation == "":
            #If no save path selected display error
            QMessageBox.critical(self, "Missing folder path", "No folder path selected.")
            #Remove text from save box
            self.txtSaveLocation.setText('')
            return
        
        #Update text box with save location
        self.txtSaveLocation.setText(f'{self.acquisitionSaveLocation}')

        #Update save location in ML pipeline
        self.mainPipeline.setSaveLocation(self.acquisitionSaveLocation)
        pass


    def updateContrastSettings(self):
        #Get values of min slider
        self.minContrastValue = self.sliderContrastMin.value()
        #Get value of max slider
        self.maxContrastValue = self.sliderContrastMax.value()

        #Check min is below max
        if self.minContrastValue >= self.maxContrastValue:
            #Set min value to max minus 1 
            self.minContrastValue = self.maxContrastValue-1
            #Set slider position to new value
            self.sliderContrastMin.setValue(self.minContrastValue)

        #Check max is above min
        if self.maxContrastValue <= self.minContrastValue:
            #Set min value to max minus 1 
            self.maxContrastValue = self.minContrastValue+1
            #Set slider position to new value
            self.sliderContrastMax.setValue(self.maxContrastValue)

        #Update min label
        self.lblContrastMin.setText(f'{self.minContrastValue}')
        #Update max label
        self.lblContrastMax.setText(f'{self.maxContrastValue}')

        #Pass values to post processing pipeline
        self.mainPipeline.contrastChanged(self.minContrastValue, self.maxContrastValue)
        pass

    def configureImageSelector(self):
        self.imageSlider.setMaximum(self.numberOfImages)
        self.txtRangeIndicator.setText(f'{0}/{self.numberOfImages}')

    def updateImageRangeCurrent(self):
        self.txtRangeIndicator.setText(f'{self.currentImageNo}/{self.numberOfImages}')
        self.imageSlider.setValue(self.currentImageNo)
        pass

    def btnBackPressed(self):
        #Check if at beginning of dataset
        if self.currentImageNo == 0:
            #Loop if at the beginning
            self.currentImageNo = self.numberOfImages
        else:
            #Reduce the image number by 1
            self.currentImageNo -= 1

        #Update ML pipline with new current image no
        self.mainPipeline.currentImageUpdated(self.currentImageNo)

    def sliderMoved(self):
        #Set current image number to new number
        self.currentImageNo = self.imageSlider.sliderPosition()

        #Update ML pipline number
        self.mainPipeline.currentImageUpdated(self.currentImageNo)
        pass

    def btnForwardPressed(self):
        #Check if at end of dataset
        if self.currentImageNo == self.numberOfImages:
            #Loop if at the end
            self.currentImageNo = 0
        else:
            #Increase the image number by 1
            self.currentImageNo += 1
        
        #Update ML pipline with new current image no
        self.mainPipeline.currentImageUpdated(self.currentImageNo)

    def handleToggleML(self):
        #Check if button is on or of
        #Button on -> disable ML
        if self.TFmachineLearning == True:
            self.mainPipeline.toggleML(False)
            self.TFmachineLearning = False
            self.btnEnableML.setText('ML on')

        #Button off -> enable ML
        elif self.TFmachineLearning == False:
            self.mainPipeline.toggleML(True)
            self.TFmachineLearning = True
            self.btnEnableML.setText('ML off')

        self.okayInfoText(f'Machine learning set to {self.TFmachineLearning}')

    def handleToggleDemo(self):
        #Check the stack of the demo toggle
        TFDemo = self.ckbToggleDemo.isChecked()
        try:
            #Send state to main pipeline
            self.mainPipeline.toggleDemo(TFDemo)
            #Set camera frame to 256x256
            self.mainPipeline.setCameraFrameSize(256,256,0,0)
            #Update cameraframe info
            self.updateCameraFrameInfo()
            #Display okay text
            self.okayInfoText(f'Demo mode set to {TFDemo}')
        except:
            self.errorInfoText('Error changing demo mode')

    def initaliseCamera(self):
        #CAMERA INITALISATION
        self.cameraInitialised = self.mainPipeline.initaliseCamera() #Initialise camera
        #If the camera fails to initalised display error
        if self.cameraInitialised == False:
            self.errorInfoText('Error initalising camera')
            return
        
        #Enable demo mode toggle
        self.ckbToggleDemo.setEnabled(True)

        #Enable de-init button
        self.btnDeInitaliseCamera.setEnabled(True)

        #Disable init button
        self.btnInitaliseCamera.setEnabled(False)
        
        #Update camera info
        self.txtCameraSN.setText(f'{self.mainPipeline.cameraFunctions.cameraSerialNum}')
        self.txtCameraName.setText(f'{self.mainPipeline.cameraFunctions.cameraModelName}')

        #Update camera frame info
        self.updateCameraFrameInfo()

        #Change max and min x and y axis of frame
        self.numFrameX.setMaximum(self.mainPipeline.cameraFunctions.maxWidth)
        self.numFrameX.setMinimum(self.mainPipeline.cameraFunctions.minWidth)
        self.numFrameX.setSingleStep(self.mainPipeline.cameraFunctions.widthIncrements)

        self.numFrameY.setMaximum(self.mainPipeline.cameraFunctions.maxHeight)
        self.numFrameY.setMinimum(self.mainPipeline.cameraFunctions.minHeight)
        self.numFrameY.setSingleStep(self.mainPipeline.cameraFunctions.heightIncrements)

        #Enable capture button
        self.btnCapture.setEnabled(True)

        self.okayInfoText('Camera initalised')

    def deInitaliseCamera(self):
        #Check is camera is imaging
        if self.playTF == True: #True = camera not imaging
            #De-init camera
            self.mainPipeline.cameraFunctions.endAcquisition()
            #Enable init camera button
            self.btnInitaliseCamera.setEnabled(True)
            #Disable deinit button
            self.btnDeInitaliseCamera.setEnabled(False)
        else:
            self.errorInfoText("Make sure the camera isn't imaging")

    def setCameraFrameSize(self):
        self.newXFrameSize = self.numFrameX.value()
        self.newYFrameSize = self.numFrameY.value()
        self.newXFrameOffset = self.numFrameXOffset.value()
        self.newYFrameOffset = self.numFrameYOffset.value()
        #Try updating camera frame size
        TFCameraFrame = self.mainPipeline.setCameraFrameSize(self.newXFrameSize, self.newYFrameSize, self.newXFrameOffset, self.newYFrameOffset)
        if TFCameraFrame:
            pass
        else:
            #If frame can't be changed display error
            self.errorInfoText('Error updating frame')

        #Update camera frame info
        self.updateCameraFrameInfo()

    def updateCameraFrameInfo(self):
        #Set current frame text
        self.lblCurrentFrameX.setText(f'X: {self.mainPipeline.cameraFunctions.currentWidth}')
        self.lblCurrentFrameXOffset.setText(f'X Offset: {self.mainPipeline.cameraFunctions.currentOffsetX}')

        self.lblCurrentFrameY.setText(f'Y: {self.mainPipeline.cameraFunctions.currentheight}')
        self.lblCurrentFrameYOffset.setText(f'Y Offset: {self.mainPipeline.cameraFunctions.currentOffsetY}')

    def updateCurrentFrameSize(self, width, height, xOffset, yOffset):
        #Update labels to display new frame size
        self.lblCurrentFrameX.setText(f'X: {width}')
        self.lblCurrentFrameY.setText(f'X: {height}')
        self.lblCurrentFrameXOffset.setText(f'X: {xOffset}')
        self.lblCurrentFrameYOffset.setText(f'X: {yOffset}')

        #Display okay message
        self.okayInfoText('Frame size updated')

    def handlePlayPause(self):
        # try:
        if self.playTF==True:
            self.beginPlayback.emit() #Emit signal to begin thread
            #Set button to display stop
            self.btnPlayPause.setText('Stop')
            self.playTF = False
            print('starting playing in ML mode')
        else:
            self.mainPipeline.stopPlayback()
            #Change button to display Play
            self.btnPlayPause.setText('Play')
            self.playTF = True
            print('ML playback paused')

        # except:
        #     QMessageBox.critical(self, "Error playing dataset", "Error playing dataset. \nMake sure a dataset is selected and try again.")
        pass

    def handleAcquisition(self):
        if self.playTF==True:
            self.beginAcquisition.emit() #Emit signal to begin thread
            #Set button to display stop
            self.btnCapture.setText('Stop')
            self.playTF = False

            #Disable set frame button
            self.btnSetCameraFrame.setEnabled(False)

            #Disable demo toggle
            self.ckbToggleDemo.setEnabled(False)

        else:
            self.mainPipeline.stopAcquisition()
            #Change button to display Play
            self.btnCapture.setText('Capture')
            self.playTF = True

            #Re enable set frame size
            self.btnSetCameraFrame.setEnabled(True)

            #Re enable demo toggle
            self.ckbToggleDemo.setEnabled(True)

    def toggleRecording(self):
        if self.recordTF == True: #True = is recording
            #Stop recording
            self.mainPipeline.stopRecording()
            #Change recordTF to False
            self.recordTF = False
            #Update button text
            self.btnRecord.setText('Start recording')
            pass

        elif self.recordTF == False: #False = isn't recording
            #Check if save location is set
            if self.acquisitionSaveLocation != '':
                #Start recording
                if self.mainPipeline.startRecording():
                    #Change recordTF to True
                    self.recordTF = True
                    #Update button text
                    self.btnRecord.setText('Stop recording')
                    #Enable save button if a location is set and recording enabled
                    self.btnSave100.setEnabled(True)
                else:
                    self.errorInfoText('Error starting recording, make sure a ML model is loaded')
            else:
                self.errorInfoText('No save location set')

    def handleSaveImages(self):
        #Tell main pipeline to save images in save stack
        try:
            self.mainPipeline.saveImageStack()
            self.okayInfoText(f'Images tack saved to {self.acquisitionSaveLocation}')
        except:
            self.errorInfoText('Error saving images')


    def updateDisplayPlayback(self,imgOut, imageNo):
        #Clear previous image from scene
        self.imageSingleScene.clear()
        #Add the pixmap of the new image to the scene
        self.imageSingleScene.addPixmap(imgOut.scaled(1080,720, aspectRatioMode=Qt.KeepAspectRatio))
        #Tell the scene to update
        self.imageSingleScene.update()
        #Set the display to the new scene
        self.imageSingleDisplay.setScene(self.imageSingleScene)

        #Update the current image number
        self.currentImageNo = imageNo
        self.updateImageRangeCurrent()

        pass

    def updateDisplayCamera(self, imgOut):
        #Clear previous image from scene
        self.imageSingleScene.clear()
        #Add the pixmap of the new image to the scene
        self.imageSingleScene.addPixmap(imgOut.scaled(1080,720, aspectRatioMode=Qt.KeepAspectRatio))
        #Tell the scene to update
        self.imageSingleScene.update()
        #Set the display to the new scene
        self.imageSingleDisplay.setScene(self.imageSingleScene)
        pass



    def disableAllButtons(self):
        #Disable all buttons while loading...
        pass

    def errorInfoText(self, text):
        self.txtInfo.setStyleSheet("QLineEdit { background-color : red; color : blue; }")
        self.txtInfo.setText(text)

    def okayInfoText(self, text):
        self.txtInfo.setStyleSheet("QLineEdit { background-color : none; color : white; }")
        self.txtInfo.setText(text)

    def createErrorMessage(self,text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText(text)
        msg.setWindowTitle("Error")
        msg.exec_()



         
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
    window = WidgetGallery()
    window.show()
    sys.exit(app.exec_())