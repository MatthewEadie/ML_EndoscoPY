#Beginning of GUI for python version of versi player


from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import os

from playbackPipeline import playbackMethod
# from cameraSettings import CameraThread
from DisplaySettings import displaySettings
from initImagingSession import newImagingSession

try:
    from machineLearningPipeline import machineLearningPipeline
except:
    print('Could not initalise ML pipeline')

import numpy as np

# import nidaqmx
# from nidaqmx.constants import AcquisitionType



class WidgetGallery(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(50, 50, 1100, 750)
        self.setWindowTitle("Styles")


        self.selectedExposure = 25
        self.selectedDataset= ''
        self.datasetFilepath = ''


        # create tool bar (Menu, Export, Help)
        self.createMenuBar()

        #Two columns
        #Left column - Main display with two tabs
            #- single image display
            #- multi image display

        #Right column - application settings (3 rows)
        #first row - image settings
            #- calculation method
            # Exposure time
            # image file

        #Second row - Channel settings
            #two tabs 
                #- channel settings
                    #3 columns
                        #Blue settings
                        #Red settings
                        #NIR settings
                # colourmap   

        self.mainWindow = Window()
        self.setCentralWidget(self.mainWindow)


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


    def openFile(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dialog.setViewMode(QFileDialog.ViewMode.List)
        self.directoryPath = dialog.getExistingDirectory()


        if self.directoryPath == "":
            QMessageBox.critical(self, "Missing folder path", "No folder path selected.")
            return

        dirCheck = self.mainWindow.checkDirectoryFolders(self.directoryPath)
        if (dirCheck == False):
            return    
        else:
            #add imaging datasets to Qlistview
            self.mainWindow.newSessionOpened(self.directoryPath)
            #self.mainWindow.lstDatasetList
            pass
        

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

        self.dataset_filepath = QFileDialog.getOpenFileName(self, "Open File", "./", "Numpy array (*.npy)")[0]

        # dialog = QFileDialog(self, "Open dataset", "Image Files (*.npy)")
        # dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        # dialog.setViewMode(QFileDialog.ViewMode.List)
        # self.datasetDirectoryPath = dialog.getExistingDirectory()


        if self.dataset_filepath == "":
            QMessageBox.critical(self, "Missing folder path", "No folder path selected.")
            return
        
        self.mainWindow.newMLDatasetOpened(self.dataset_filepath)




























class Window(QWidget):
    beginCapture = pyqtSignal()
    beginPlayback = pyqtSignal()
    beginMLPlayback = pyqtSignal()

    cameraInitialised = True

    def __init__(self):
        super().__init__()
        self.setWindowTitle("QGridLayout Example")


        #----- GLOBAL VARIABLES -----
        self.imageSingleScene = QGraphicsScene()


        #Black large display
        self.displayImage = np.zeros((720,1080))
        height, width = self.displayImage.shape
        bytesPerLine = 3*width
        self.displayImage = QImage(self.displayImage.data, width, height, bytesPerLine, QImage.Format_Grayscale8)
        self.displayImage = QPixmap.fromImage(self.displayImage)
        self.imageSingleScene.addPixmap(self.displayImage)




        self.sessionDirectory = ""

        self.playTF = True #Initalise play stop button as true

        self.globalDisplayMode = 1 # 1 = playback, 2 = acquisition



        self.playbackPipeline = playbackMethod()
        self.processingThread = QThread()
        self.playbackPipeline.moveToThread(self.processingThread)
        self.processingThread.start() #Starting thread as playback is default on start

        # self.cameraFunctions = CameraThread()
        # self.cameraThread = QThread()
        # self.cameraFunctions.moveToThread(self.cameraThread)

        self.MLPipeline = machineLearningPipeline()
        self.MLThread = QThread()
        self.MLPipeline.moveToThread(self.MLThread)

        #SIGNALS
        # self.beginCapture.connect(self.cameraFunctions.run_single_camera)
        self.beginMLPlayback.connect(self.MLPipeline.runML)
        

        #SLOTS
        # self.cameraFunctions.imageAcquired.connect(self.updateSingleDisplay)
        # self.cameraFunctions.updateFPS.connect(self.fpsCounter)

        self.MLPipeline.updateImageML.connect(self.handleSingleImageProcessed)
        #----------------------------



        # Create a QGridLayout instance
        layout = QGridLayout()

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

        #Connect buttons to functions when clicked
        self.radioMLMode.clicked.connect(self.changeDisplayMode)
        self.radioAcquisitionMode.clicked.connect(self.changeDisplayMode)

        #Add the mode selection onto main page layout
        layout.addWidget(self.modeSelectionGroup,0,0)


        


        self.singleDisplay = QWidget()
        singleDisplayLayout = QGridLayout()
        self.singleDisplay.setLayout(singleDisplayLayout)

        self.imageSingleDisplay = QGraphicsView()
        self.imageSingleDisplay.setScene(self.imageSingleScene)
        # self.imageSingleDisplay.setPixmap(self.displayImage.scaled(1080,720, aspectRatioMode=Qt.KeepAspectRatio))
        # self.imageSingleDisplay.setStyleSheet("border: 1px solid black;")

        singleDisplayLayout.addWidget(self.imageSingleDisplay,0,0)

        layout.addWidget(self.singleDisplay,1,0,5,5)


        #Group layout for dataset list
        self.grpSessionSettings = QGroupBox()
        groupLayout = QGridLayout()
        self.grpSessionSettings.setLayout(groupLayout)

        #List widget for datasets in selected folder
        self.lstDatasetList = QListWidget()
        self.btnSelectDataset = QPushButton("Select dataset")
        self.btnSelectDataset.clicked.connect(self.loadDataset)

        #Add dataset list widget to layout
        groupLayout.addWidget(self.lstDatasetList, 0, 2, 2, 2)
        groupLayout.addWidget(self.btnSelectDataset, 3, 2)

        #Add dataset layout to main layout
        layout.addWidget(self.grpSessionSettings,1,5)



        #----- CONTRAST AND COLOURMAP TAB -----
        self.settingsTabs = QTabWidget()

        self.createContrastTab()
        self.settingsTabs.addTab(self.contrastTab, "Contrast")

        self.createMachineLearningTab()
        self.settingsTabs.addTab(self.machineLearningTab, "ML settings")

        self.createCameraTab()
        self.settingsTabs.addTab(self.cameraSettingsTab, "Camera Settings")

        


        # PLAY PAUSE BUTTON TO BEGIN PROCESSING
        self.btnPlayPause = QPushButton('Play')
        self.btnPlayPause.clicked.connect(self.handlePlayPause)

        # Add widgets to the layout
        layout.addWidget(self.grpSessionSettings,1,5,1,2)
        layout.addWidget(self.settingsTabs, 2,5,1,2)
        layout.addWidget(self.btnPlayPause, 3,5)



        #IMAGE SELECTOR
        self.start_slider = QSlider(orientation=Qt.Horizontal)
        self.start_slider.setMinimum(1)
        self.start_slider.setMaximum(4000)
        self.start_slider.setAutoFillBackground(False)
        # self.start_slider.setStyleSheet(
        #     "QSlider::groove:horizontal, QSlider::groove:horizontal:hover, QSlider::sub-page:horizontal, QSlider::groove:horizontal:disabled { border:0;  background: #19232D; }")
        
        # self.end_slider = QSlider(orientation=Qt.Horizontal)
        # self.end_slider.setMinimum(1)
        # self.end_slider.setMaximum(4000)
        # self.end_slider.setValue(4000)
        # self.end_slider.setAutoFillBackground(False)
        # self.end_slider.setStyleSheet("QSlider::groove:horizontal, QSlider::groove:horizontal:hover, QSlider::sub-page:horizontal, QSlider::groove:horizontal:disabled { border:0;  background: #19232D; }")
        

        # self.rangeIndicator = QLabel()
        # self.rangeIndicator.setFixedHeight(25)
        # self.rangeIndicator.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

        
        # layout.addWidget(self.start_slider, 6, 0, 1, 5)
        # layout.addWidget(self.rangeIndicator, 7, 0, 1, 5)
        # layout.addWidget(self.end_slider, 8, 0, 1, 5)

        # self.updateRangeIndicator()

        # LABEL FOR USING INFORMATION
        self.txtInfo = QLabel('info text')
        layout.addWidget(self.txtInfo,9,0,1,0)

        self.txtFPS = QLabel('fps counter')
        self.txtFPS.setAlignment(Qt.AlignRight)
        layout.addWidget(self.txtFPS,9,4)

        #DISPLAY SIGNALS AND SLOTS
        self.checkBlueNormalise.clicked.connect(self.updateImageSettings)
        self.checkBlueSubtrackBkg.clicked.connect(self.updateImageSettings)
        self.checkBlueAutoContrast.clicked.connect(self.updateImageSettings)
        self.btnBlueChannelOnOff.clicked.connect(self.updateImageSettings)


        #PROCESSING METHOD SIGNALS AND SLOTS
        self.radioBlueBasic.clicked.connect(self.updateImageSettings)
        self.radioBlueGaussian.clicked.connect(self.updateImageSettings)
        self.radioBlueInterpolation.clicked.connect(self.updateImageSettings)
        self.radioBlueBinning.clicked.connect(self.updateImageSettings)


        #SIGNALS AND SLOTS FOR CONTRAST SETTINGS
        self.sliderBlueMin.valueChanged.connect(self.updateImageSettings)
        self.sliderBlueMax.valueChanged.connect(self.updateImageSettings)



        



        # #CAMERA INITALISATION
        # if self.cameraFunctions.initialise(): #Initialise camera
        #         self.cameraInitialised = True
        # else:
        #     self.createErrorMessage('No camera detected, starting without acqisition mode.')
        #     # print('Error initalising camera!')
        #     self.cameraInitialised = False
        #     self.disableCameraOptions()
        #     #ADD FUNCTION TO DISABLE CAMERA SETTING IF NOT INITIALISED

        # #TRIGGERING
        # try:
        #     self.task = nidaqmx.Task()
        # except:
        #     print('Error connecting to trigger unit')
        #     self.createErrorMessage('No trigger unit detected, starting without acqisition mode.')
        #     self.disableCameraOptions()

        #SET DEFAULT VALUES AT END OF WIDGET ALLOCATIONS
        #----------------------------------------------
        self.radioExposure25.setChecked(True) #Program default exposure setting is 25ms


        #----------------------------------------------

        # Set the layout on the application's window
        self.setLayout(layout)

        #Initalise all settings on open
        self.updateImageSettings() 

    def changeDisplayMode(self):
        displayMode = self.modeButtonGroup.checkedId()
        if displayMode == 1:
            self.globalDisplayMode = 1
            self.processingThread.start()
            self.cameraThread.exit() #End camera thread when swapping to playback
            print('Playback mode')
        elif displayMode == 2:
            self.globalDisplayMode = 2
            self.cameraThread.start() #Creates thread for camera acquisition
            self.processingThread.exit() #End playback thread
            print('Acquisition mode')
        elif displayMode == 3:
            self.globalDisplayMode = 3
            self.MLThread.start()
            print('Machine learning mode')
        else:
            print('Error setting display mode')

    def disableCameraOptions(self):
        self.txtInfo.setText('No camera detected, disabling camera options.') # change to popup error message
        self.radioAcquisitionMode.setEnabled(False) # Disable radio button for acquisition mode
        self.triggerModeSelection.setEnabled(False) # Disable trigger mode settings as without a camera the triggering isn't needed
        pass

    def changeTriggerMode(self):
        selectredTriggerMode = self.triggerModeSelectionGroup.checkedId()
        if selectredTriggerMode == 1:
            self.triggerMode = 1

            try:
                self.task.close() #Delete the trigger task
            except:
                print('No task to close')

            self.cameraFunctions.setTrigger(1)
            print('Trigger mode set to software')
        elif selectredTriggerMode == 2:
            self.triggerMode = 2
            self.cameraFunctions.setTrigger(2)

            self.createTriggerTask()#Create a trigger task using selected exposuretime

            print('Trigger mode set to hardware')
        else:
            print('Error changing trigger mode.')






    def createContrastTab(self):
        self.contrastTab = QWidget()
        self.contrastTabLayout = QHBoxLayout()
        self.contrastTab.setLayout(self.contrastTabLayout)

        self.contrastLabelFont = QFont('Arial', 15)
        self.contrastLabelFont.setBold(True)

        #----- BLUE CHANNEL GUI -----
        self.grpBlueChannel = QGroupBox('Blue/Green')
        self.grpBlueChannelLayout = QVBoxLayout()
        self.grpBlueChannel.setLayout(self.grpBlueChannelLayout)

        self.grpBlueProcesingSteps = QGroupBox('Processing steps')
        self.grpBlueProcesingStepsLayout = QVBoxLayout()
        self.grpBlueProcesingSteps.setLayout(self.grpBlueProcesingStepsLayout)
        self.checkBlueSubtrackBkg = QCheckBox('Subtract Background')
        self.checkBlueNormalise = QCheckBox('Normalise')
        self.grpBlueProcesingStepsLayout.addWidget(self.checkBlueSubtrackBkg,)
        self.grpBlueProcesingStepsLayout.addWidget(self.checkBlueNormalise)
        self.grpBlueChannelLayout.addWidget(self.grpBlueProcesingSteps)

        self.grpBlueDisplay = QGroupBox('Display')
        self.grpBlueDisplayLayout = QVBoxLayout()
        self.grpBlueDisplay.setLayout(self.grpBlueDisplayLayout)
        #btn grp
        self.btngrpBlueDisplay = QButtonGroup()
        self.radioBlueBasic = QRadioButton('Basic')
        self.radioBlueBasic.setChecked(True)
        self.radioBlueGaussian = QRadioButton('Gaussian')
        self.radioBlueInterpolation = QRadioButton('Interpolation')
        self.radioBlueBinning = QRadioButton('Binning')

        self.btngrpBlueDisplay.addButton(self.radioBlueBasic,1)
        self.btngrpBlueDisplay.addButton(self.radioBlueGaussian,2)
        self.btngrpBlueDisplay.addButton(self.radioBlueInterpolation,3)
        self.btngrpBlueDisplay.addButton(self.radioBlueBinning,4)


        self.grpBlueDisplayLayout.addWidget(self.radioBlueBasic)
        self.grpBlueDisplayLayout.addWidget(self.radioBlueGaussian)
        self.grpBlueDisplayLayout.addWidget(self.radioBlueInterpolation)
        self.grpBlueDisplayLayout.addWidget(self.radioBlueBinning)

        self.grpBlueChannelLayout.addWidget(self.grpBlueDisplay)

        self.grpBlueSliders = QGroupBox('Contrast')
        self.grpBlueSlidersLayout = QHBoxLayout()
        self.grpBlueSliders.setLayout(self.grpBlueSlidersLayout)
        self.sliderBlueMin = QSlider()
        self.sliderBlueMin.setMaximum(255)
        self.sliderBlueMin.setMinimum(0)
        self.sliderBlueMax = QSlider()
        self.sliderBlueMax.setMaximum(255)
        self.sliderBlueMax.setMinimum(0)
        self.sliderBlueMax.setValue(255)
        self.lblBlueMin = QLabel('0')
        self.lblBlueMin.setFont(self.contrastLabelFont)
        self.lblBlueMax = QLabel('255')
        self.lblBlueMax.setFont(self.contrastLabelFont)
        self.grpBlueSlidersLayout.addWidget(self.lblBlueMin)
        self.grpBlueSlidersLayout.addWidget(self.sliderBlueMin)
        self.grpBlueSlidersLayout.addWidget(self.sliderBlueMax)
        self.grpBlueSlidersLayout.addWidget(self.lblBlueMax)
        self.grpBlueChannelLayout.addWidget(self.grpBlueSliders)

        self.checkBlueAutoContrast = QCheckBox('Auto contrast')
        self.btnBlueChannelOnOff = QPushButton('ON')
        self.btnBlueChannelOnOff.setCheckable(True)
        self.btnBlueChannelOnOff.setChecked(True)
        self.grpBlueChannelLayout.addWidget(self.checkBlueAutoContrast)
        self.grpBlueChannelLayout.addWidget(self.btnBlueChannelOnOff)

        #----- CONTRAST TEB GUI -----
        self.contrastTabLayout.addWidget(self.grpBlueChannel)

    def createCameraTab(self):
        # TRIGGER MODE SETTINGS # 
        #Layout for entire camera settings tab
        self.cameraSettingsTab = QWidget()
        self.cameraSettingsLayout = QVBoxLayout()
        self.cameraSettingsTab.setLayout(self.cameraSettingsLayout)

        #Layout for trigger mode selector
        self.triggerModeSelection = QGroupBox()
        self.triggerModeSelectionLayout = QHBoxLayout()
        self.triggerModeSelection.setLayout(self.triggerModeSelectionLayout)

        #Create radio buttons for mode selector
        self.triggerModeSelectionGroup = QButtonGroup()
        self.softwareTrigger = QRadioButton('Software')
        self.softwareTrigger.setChecked(True)
        self.hardwareTrigger = QRadioButton('Hardware')

        #Add buttons to group for radio to function
        self.triggerModeSelectionGroup.addButton(self.softwareTrigger,1)
        self.triggerModeSelectionGroup.addButton(self.hardwareTrigger,2)

        #Add buttons to mode selector layout
        self.triggerModeSelectionLayout.addWidget(self.softwareTrigger)
        self.triggerModeSelectionLayout.addWidget(self.hardwareTrigger)

        #Connect buttons to functions
        self.softwareTrigger.clicked.connect(self.changeTriggerMode)
        self.hardwareTrigger.clicked.connect(self.changeTriggerMode)

        #Add trigger mode to tab layout
        self.cameraSettingsLayout.addWidget(self.triggerModeSelection)


        # EXPOSURE SETTINGS #
        #Layout for exposure settings
        groupExposureSettings = QGroupBox()
        groupExposureSetLayout = QVBoxLayout()
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
        groupExposureSetLayout.addWidget(self.radioExposure5)
        groupExposureSetLayout.addWidget(self.radioExposure15)
        groupExposureSetLayout.addWidget(self.radioExposure25)
        groupExposureSetLayout.addWidget(self.radioExposure50)

        #Connect radio buttons to functions
        self.radioExposure5.toggled.connect(self.createTriggerTask)
        self.radioExposure15.toggled.connect(self.createTriggerTask)
        self.radioExposure25.toggled.connect(self.createTriggerTask)
        self.radioExposure50.toggled.connect(self.createTriggerTask)

        #Add exposure settings group to tab layout
        self.cameraSettingsLayout.addWidget(groupExposureSettings)



    def createMachineLearningTab(self):
        self.machineLearningTab = QWidget()
        self.machineLearningTabLayout = QHBoxLayout()
        self.machineLearningTab.setLayout(self.machineLearningTabLayout)

        #Text box for ML directory

        #Text box for Dataset directory

        #Area to be populated with dataset thumbnails
        pass

    def newSessionOpened(self, directoryPath):
        self.sessionDirectory = directoryPath
        self.sessionImagingPath = f'{self.sessionDirectory}/Imaging Data/'

        datasetFolders = os.listdir(self.sessionImagingPath)

        #DO WE NEED TO SPLIT THESE????
        # datasetDates = []
        # datasetTimes = []
        # for dataset in datasetFolders:
        #     datasetDates.append(dataset.split('_')[0])
        #     datasetTimes.append(dataset.split('_')[1])

        self.lstDatasetList.clear() # remove previous entries
        self.lstDatasetList.addItems(datasetFolders)

        #Calibration image location
        # sesstionCalibrationPath = directoryPath + /Calibration Data/
        # loop for each exposure (5, 15, 25, 50, 100, 250) (Only 25ms to start)
        # in each loop for each colour channel (only Blue to start)
        # send calibration images to processing class global variables

        tfNewSession = self.playbackPipeline.newSession(folderPath=self.sessionDirectory)
        if tfNewSession:
            self.txtInfo.setText('New session opened.')
        else:
            self.txtInfo.setText('Error opening new session.')

    def newMLModelOpened(self, MLDirectoryPath):
        # read in model path
        try:
            self.MLPipeline.loadModel(MLDirectoryPath)
        except:
            print('Error loading ML model')
        # set class variable model path to selected path
        # set text field in ML settings to path
        pass

    def newMLDatasetOpened(self, datasetPath):
        # Check file is .npy
        try:
            self.MLPipeline.loadDataset(datasetPath)
        except:
            print('Error loading chosen dataset')
        # Set class variable dataset path to selected path
        # Set text field in ML settings
        pass

    def createTriggerTask(self):
        # try:
            # try:
            #     self.task.close() #clear any previous task
            # except:
            #     print('no task to close')

            # newExposure = self.btngrpExposure.checkedId()/1000 #change to milliseconds
            # print(newExposure)

            # self.task = nidaqmx.Task()
            # self.task.co_channels.add_co_pulse_chan_time("cDAQ_VER/ctr0",initial_delay=0.0, low_time=newExposure, high_time=newExposure) #I/O channel 0 
            # self.task.co_channels.add_co_pulse_chan_time("cDAQ_VER/ctr1",initial_delay=0.0, low_time=newExposure, high_time=newExposure) #I/O channel 3
            # # task.co_channels.add_co_pulse_chan_time("cDAQ_VER/ctr2",initial_delay=0.0, low_time=0.5, high_time=0.5) #I/O channel 1 
            # # task.co_channels.add_co_pulse_chan_time("cDAQ_VER/ctr3",initial_delay=0.1, low_time=0.15, high_time=0.05) I/O channel 2
            # self.task.timing.cfg_implicit_timing(sample_mode=AcquisitionType.CONTINUOUS)
            # # self.task.timing.cfg_implicit_timing(sample_mode=AcquisitionType.FINITE, samps_per_chan=10)
            # print('trigger set')
        # except:
        #     self.txtInfo.setText('Error setting trigger task.')
        print('Error setting trigger task.')

    def startTriggering(self):
        try:
            self.task.start()
            print('starting trigger')
        except:
            print('Error start Task')

    def stopTriggering(self):
        try:
            self.task.stop() #clear any previous task
        except:
            print('Task could not be stopped')

        # while(not(self.task.is_task_done())):
        #         self.task.is_task_done()
        
        
    def settingChanged(self):
        #Change setting to use Manual or from Metadata settings
        pass


    def checkDirectoryFolders(self, folderPath):
        checkCalibTF = False
        checkGeneratedTF = False
        checkImagingTF = False

        checkCalibTF = os.path.isdir(folderPath+'/Calibration Data')
        checkGeneratedTF = os.path.isdir(folderPath+'/Generated Data')
        checkImagingTF = os.path.isdir(folderPath+'/Imaging Data')

        if (checkCalibTF == False):
            QMessageBox.critical(self, "Missing calibration folder", "The calibration data folder could not be found at the selected location.")
            return False

        if (checkGeneratedTF == False):
            QMessageBox.critical(self, "Missing generated folder", "The generated data folder could not be found at the selected location.")
            return False
            
        if (checkImagingTF == False):
            QMessageBox.critical(self, "Missing imaging folder", "The imaging data folder could not be found at the selected location.")
            return False

        return True
    

    def loadDataset(self):
        #get selected item
        try:
            selectedDataset = self.lstDatasetList.currentItem()
            self.txtInfo.setText(selectedDataset.text())
            self.playbackPipeline.updateSelectedDataset(selectedDataset.text())
        except:
            self.txtInfo.setText('No dataset selected.')
        
        return

        

        #imaging path = self.directory+date+dataset
        #send path to imaging pipeline

        #open imaging session from selected dataset from listview
        pass


    def handlePlayPause(self):
        # self.globalDisplayMode:   1 - Playback   2 - Camera   3 - Machine learning
        if self.globalDisplayMode == 1:
        # try:
            if self.playTF==True:
                self.beginPlayback.emit() #Tell playback thread to run

                #Set button to display stop
                self.btnPlayPause.setText('Stop')
                self.playTF = False
                print(f'Play pressed - TF = {self.playTF}')
            else:
                self.playbackPipeline.endPlayback()

                #Change button to display Play
                self.btnPlayPause.setText('Play')
                self.playTF = True
                print(f'Stop pressed - TF = {self.playTF}')
                pass

        # elif self.globalDisplayMode == 2:
        #     if self.playTF==True:
        #         self.beginCapture.emit() #Emit signal to begin thread
        #         self.startTriggering()
        #         #Set button to display stop
        #         self.btnPlayPause.setText('Stop')
        #         self.playTF = False

        #     else:
        #         self.cameraFunctions.exit()
        #         self.stopTriggering()
        #         #Change button to display Play
        #         self.btnPlayPause.setText('Play')
        #         self.playTF = True

        elif self.globalDisplayMode == 3:
            print('starting playing in ML mode')
            if self.playTF==True:
                self.beginMLPlayback.emit() #Emit signal to begin thread
                #Set button to display stop
                self.btnPlayPause.setText('Stop')
                self.playTF = False

            else:
                self.MLPipeline.stopMLPlayback()
                #Change button to display Play
                self.btnPlayPause.setText('Play')
                self.playTF = True
        else:
            print('unknown playback option.')


        # except:
        #     QMessageBox.critical(self, "Error playing dataset", "Error playing dataset. \nMake sure a dataset is selected and try again.")
        pass

    def updateSingleDisplay(self, imagePixmap):
        self.imageSingleScene.clear()
        self.imageSingleScene.addPixmap(imagePixmap.scaled(1080,720, aspectRatioMode=Qt.KeepAspectRatio))
        self.imageSingleScene.update()

        self.imageSingleDisplay.resetTransform()

        self.imageSingleDisplay.setScene(self.imageSingleScene)
        # self.imageSingleDisplay.setSceneRect(1080,720)
        # self.imageSingleDisplay.scale(256,256)
        # self.imageSingleDisplay.fitInView(self.imageScene.sceneRect(), Qt.KeepAspectRatio)
        self.imageSingleDisplay.setAlignment(Qt.AlignCenter)
        self.imageSingleDisplay.show()
        # self.imageSingleDisplay.setPixmap(imagePixmap.scaled(1080,720, aspectRatioMode=Qt.KeepAspectRatio))


    def handleImageProcessed(self, imgOut_Combined, imgOut_Red, imgOut_Blue, imgOut_NIR):

        print('image emitted')

        self.imageSingleScene.clear()
        self.imageSingleScene.addPixmap(imgOut_Combined.scaled(1080,720, aspectRatioMode=Qt.KeepAspectRatio))
        self.imageSingleScene.update()
        self.imageSingleDisplay.setScene(self.imageSingleScene)

        self.imageCombinedScene.clear()
        self.imageGreenScene.clear()
        self.imageRedScene.clear()
        self.imageNIRScene.clear()

        self.imageCombinedScene.addPixmap(imgOut_Combined.scaled(540,360, aspectRatioMode=Qt.KeepAspectRatio))
        self.imageGreenScene.addPixmap(imgOut_Blue.scaled(540,360, aspectRatioMode=Qt.KeepAspectRatio))
        self.imageRedScene.addPixmap(imgOut_Red.scaled(540,360, aspectRatioMode=Qt.KeepAspectRatio))
        self.imageNIRScene.addPixmap(imgOut_NIR.scaled(540,360, aspectRatioMode=Qt.KeepAspectRatio))

        self.imageCombinedScene.update()
        self.imageGreenScene.update()
        self.imageRedScene.update()
        self.imageNIRScene.update()

        self.imageTopLeftDisplay.setScene(self.imageCombinedScene)
        self.imageTopRightDisplay.setScene(self.imageGreenScene)
        self.imageBottomLeftDisplay.setScene(self.imageRedScene)
        self.imageBottomRightDisplay.setScene(self.imageNIRScene)



        # height, width, channels = imgOut_Combined.shape
        # bytesPerLine = 3*width

        # arrCombined = np.require(imgOut_Combined, np.uint8, 'C')
        # arrRed = np.require(imgOut_Red, np.uint8, 'C')
        # arrBlue = np.require(imgOut_Blue, np.uint8, 'C')
        # arrNIR = np.require(imgOut_NIR, np.uint8, 'C')

        # qImg = QImage(arrCombined.data, width, height, bytesPerLine, QImage.Format_RGB888)
        # pixmap = QPixmap.fromImage(qImg)
        # self.imageSingleDisplay.setPixmap(pixmap.scaled(1080,720, aspectRatioMode=Qt.KeepAspectRatio))

        # #multi dsiplay merged image
        # qImg = QImage(arrCombined.data, width, height, bytesPerLine, QImage.Format_RGB888)
        # pixmap = QPixmap.fromImage(qImg)
        # self.imageTopLeftDisplay.setPixmap(pixmap.scaled(540,360, aspectRatioMode=Qt.KeepAspectRatio)) #Small multi display (combined image)

        # qImgBlue = QImage(arrBlue.data, width, height, bytesPerLine, QImage.Format_RGB888)
        # pixmapBlue = QPixmap.fromImage(qImgBlue)
        # self.imageTopRightDisplay.setPixmap(pixmapBlue.scaled(540,360, aspectRatioMode=Qt.KeepAspectRatio))

        # qImgRed = QImage(arrRed.data, width, height, bytesPerLine, QImage.Format_RGB888)
        # pixmapRed = QPixmap.fromImage(qImgRed)
        # self.imageBottomLeftDisplay.setPixmap(pixmapRed.scaled(540,360, aspectRatioMode=Qt.KeepAspectRatio))

        # qImgNIR = QImage(arrNIR.data, width, height, bytesPerLine, QImage.Format_RGB888)
        # pixmapNIR = QPixmap.fromImage(qImgNIR)
        # self.imageBottomRightDisplay.setPixmap(pixmapNIR.scaled(540,360, aspectRatioMode=Qt.KeepAspectRatio))

    def handleSingleImageProcessed(self,imgOut): #Duplicate function of updateSingleDisplay
        self.imageSingleScene.clear()
        self.imageSingleScene.addPixmap(imgOut.scaled(1080,720, aspectRatioMode=Qt.KeepAspectRatio))
        self.imageSingleScene.update()
        self.imageSingleDisplay.setScene(self.imageSingleScene)

        pass

    def updateInfoLabel(self, newText):
        self.txtInfo.setText(f'{newText}')
        return
    
    def fpsCounter(self, fps):
        self.txtFPS.setText(f'FPS: {fps}')

    # def updateImage(self, filePath):
    #     self.displayImage = QPixmap(filePath)
    #     self.updateDisplays()

    # def updateDisplays(self):
    #     self.imageSingleDisplay.setPixmap(self.displayImage.scaled(1080,720, aspectRatioMode=Qt.KeepAspectRatio))

    #     self.topLeftDisplay.setPixmap(self.displayImage.scaled(270,180, aspectRatioMode=Qt.KeepAspectRatio))
    #     self.topRightDisplay.setPixmap(self.displayImage.scaled(270,180, aspectRatioMode=Qt.KeepAspectRatio))
    #     self.bottomLeftDisplay.setPixmap(self.displayImage.scaled(270,180, aspectRatioMode=Qt.KeepAspectRatio))
    #     self.bottomRightDisplay.setPixmap(self.displayImage.scaled(270,180, aspectRatioMode=Qt.KeepAspectRatio))

    def updateImageSettings(self):
        #Blue channel settings
        # self.blueDisplaySettings.LEDisEnabled = self.btnBlueChannelOnOff.isChecked()
        # self.blueDisplaySettings.autocontrast = self.checkBlueAutoContrast.isChecked()
        # self.blueDisplaySettings.minValue = self.sliderBlueMin.value()
        # self.blueDisplaySettings.maxValue = self.sliderBlueMax.value()
        # self.blueDisplaySettings.displayMode = self.btngrpBlueDisplay.checkedId()
        # self.blueDisplaySettings.subtractBackground = self.checkBlueSubtrackBkg.isChecked()
        # self.blueDisplaySettings.normaliseByLightfield = self.checkBlueNormalise.isChecked()

        # self.playbackPipeline.setAllValues(LED_Channel=1, channelSettings=self.blueDisplaySettings)

        # self.lblBlueMin.setText(str(self.blueDisplaySettings.minValue))
        # self.lblBlueMax.setText(str(self.blueDisplaySettings.maxValue))
        # print(self.btnBlueChannelOnOff.isChecked())
        # if self.btnBlueChannelOnOff.isChecked():
        #     self.btnBlueChannelOnOff.setText("OFF")
        # else:
        #     self.btnBlueChannelOnOff.setText("ON")


        #Pass new values to processing pipeline
        print('Values changed')
        pass


    def updateRangeIndicator(self):
        """updates the range indicator that shows the subselection of the video
        for download or analysis
        """
        # Get indicator width and height
        w, h = self.rangeIndicator.width(), self.rangeIndicator.height()

        # Create an empty image to draw on
        pix = QPixmap(w, h)
        p = QPainter(pix)

        # Draw background color
        p.setBrush(QBrush(QColor("#19232D")))
        p.drawRect(-1, -1, w, h)

        # Draw foreground color
        p.setBrush(QBrush(QColor("#1464A0")))

        # Define region start and end on x axis
        x0 = w*self.start_slider.value()/self.start_slider.maximum()
        x1 = w*self.end_slider.value()/self.end_slider.maximum()

        # Draw rect from start to end of selection
        p.drawRect(int(x0), 0, int(x1-x0), h)

        # Display the number of frames selected
        p.setPen(QPen(QColor("#FFFFFF")))
        p.drawText(0, # left
            17, # center
            "{} frames selected".format(self.end_slider.value()-self.start_slider.value()+1))
        p.end()

        # Show the image
        self.rangeIndicator.setPixmap(pix)
        


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
    sys.exit(app.exec())