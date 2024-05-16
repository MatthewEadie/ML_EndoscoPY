#Beginning of GUI for python version of versi player


from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import os

from postProcessingPipeline import playbackMethod
# from cameraSettings import CameraThread
from DisplaySettings import displaySettings

try:
    from machineLearningPipeline import machineLearningPipeline
    print('ML pipeline loaded')
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


        # create tool bar
        self.createMenuBar()

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

        self.globalDisplayMode = 1 # 1 = ML playback, 2 = acquisition

        # ---- THREAD INSTANCES ---- #
        # ML THREAD #
        #Create instance of ML pipeline
        self.MLPipeline = machineLearningPipeline()
        #Create QThread to store pipeline
        self.MLThread = QThread()
        self.MLPipeline.moveToThread(self.MLThread)
        #Start the thread as ML playback is default
        self.MLThread.start()

        # CAMERA THREAD #
        # self.cameraFunctions = CameraThread()
        # self.cameraThread = QThread()
        # self.cameraFunctions.moveToThread(self.cameraThread)

        

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

        #Create software function mode (ML playback or Acquisition)
        self.createSoftwareFunctionMode()
        layout.addWidget(self.modeSelectionGroup,0,0)


        #Create display image
        self.createDisplayImage()
        layout.addWidget(self.singleDisplay,1,0,5,5)


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

        #Add dataset layout to main layout
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
        self.btnPlayPause = QPushButton('Play')
        self.btnPlayPause.clicked.connect(self.handlePlayPause)

        # Add widgets to the layout
        layout.addWidget(self.grpSessionSettings,1,5,1,2)
        layout.addWidget(self.settingsTabs, 2,5,1,2)
        layout.addWidget(self.btnPlayPause, 3,5)



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

        #Connect buttons to functions when clicked
        self.radioMLMode.clicked.connect(self.changeDisplayMode)
        self.radioAcquisitionMode.clicked.connect(self.changeDisplayMode)

    def createDisplayImage(self):
        #Layout to contain image display
        self.singleDisplay = QWidget()
        singleDisplayLayout = QGridLayout()
        self.singleDisplay.setLayout(singleDisplayLayout)

        #Graphics view widget to display image
        self.imageSingleDisplay = QGraphicsView()
        self.imageSingleDisplay.setScene(self.imageSingleScene)

        #Add graphics view to layout
        singleDisplayLayout.addWidget(self.imageSingleDisplay,0,0)

    def changeDisplayMode(self):
        displayMode = self.modeButtonGroup.checkedId()
        if displayMode == 1:
            self.globalDisplayMode = 1
            self.MLThread.start()
            self.processingThread.start()
            self.cameraThread.exit() #End camera thread when swapping to playback
            print('Machine learning mode')
        elif displayMode == 2:
            self.globalDisplayMode = 2
            self.cameraThread.start() #Creates thread for camera acquisition
            self.processingThread.exit() #End playback thread
            print('Acquisition mode')
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
        #Initalise camera button
        self.btnInitaliseCamera = QPushButton('Initalise')
        #Add button to camera tab layout
        self.cameraSettingsLayout.addWidget(self.btnInitaliseCamera)
        #Connect button to initalise camera function
        self.btnInitaliseCamera.clicked.connect(self.initaliseCamera)



        # ---- CAMERA INFORMATION ---- #
        #Layout for camera information
        self.grpCameraInfo = QGroupBox('Camera Info')
        self.cameraInfoLayout = QHBoxLayout()
        self.grpCameraInfo.setLayout(self.cameraInfoLayout)

        #Line edit to display camera name
        self.lblCameraName = QLabel('Camera name')
        self.txtCameraName = QLineEdit()
        self.txtCameraName.setReadOnly(True)

        #Add group to tab layout
        self.cameraSettingsLayout.addWidget(self.grpCameraInfo)


        # ---- Image save location ---- # 
        #Layout for save location changing
        self.grpSaveLocation = QGroupBox('Save location')
        self.saveLocationLayout = QHBoxLayout()
        self.grpSaveLocation.setLayout(self.saveLocationLayout)

        self.btnChangeSaveLocation = QPushButton('Change save location')

        self.btnChangeSaveLocation.clicked.connect(self.changeSaveLocation)

        self.saveLocationLayout.addWidget(self.btnChangeSaveLocation)




        # ---- TRIGGER MODE SETTINGS ---- # 
        #Layout for trigger mode selector
        self.triggerModeSelection = QGroupBox('Trigger mode')
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


        # ---- EXPOSURE SETTINGS ---- #
        #Layout for exposure settings
        groupExposureSettings = QGroupBox('Exposure time (ms)')
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
            self.MLPipeline.loadModel(MLDirectoryPath)

            #Get shape of first layer
            self.firstLayerShape = self.MLPipeline.firstLayerShape
            print(self.firstLayerShape)

            #Update info box and ML tab
            self.okayInfoText('ML model loaded')
            self.txtChosenModel.setText(MLDirectoryPath)
            self.txtModelInputShape.setText(f'{self.firstLayerShape}')
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
            self.datasetShape = self.MLPipeline.loadDataset(f'{self.datasetPath}/{selectedDataset}')

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
                self.disablePlayPause()
                return

            #Display okay message in info box
            self.okayInfoText(f'Dataset loaded: {selectedDataset}')

            #Enable play/pause if disabled previously
            self.enablePlayPause()
        except:
            #Disable play/pause to avoid break
            self.disablePlayPause()

            #Display error message in info box
            self.errorInfoText('Error loading data')
        pass

    def changeSaveLocation(self):
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
        self.MLPipeline.contrastChanged(self.minContrastValue, self.maxContrastValue)
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
        self.MLPipeline.currentImageUpdated(self.currentImageNo)

    def sliderMoved(self):
        #Set current image number to new number
        self.currentImageNo = self.imageSlider.sliderPosition()

        #Update ML pipline number
        self.MLPipeline.currentImageUpdated(self.currentImageNo)
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
        self.MLPipeline.currentImageUpdated(self.currentImageNo)

    def initaliseCamera(self):
        # #CAMERA INITALISATION
        # if self.cameraFunctions.initialise(): #Initialise camera
        #         self.cameraInitialised = True
        # else:
        #     self.createErrorMessage('No camera detected, starting without acqisition mode.')
        #     # print('Error initalising camera!')
        #     self.cameraInitialised = False
        #     self.disableCameraOptions()
        #     #ADD FUNCTION TO DISABLE CAMERA SETTING IF NOT INITIALISED
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
        



    def handlePlayPause(self):
        # self.globalDisplayMode:   1 - ML Playback   2 - Camera Acquisition
        if self.globalDisplayMode == 1:
        # try:
            if self.playTF==True:
                self.beginMLPlayback.emit() #Emit signal to begin thread
                #Set button to display stop
                self.btnPlayPause.setText('Stop')
                self.playTF = False
                print('starting playing in ML mode')
            else:
                self.MLPipeline.stopMLPlayback()
                #Change button to display Play
                self.btnPlayPause.setText('Play')
                self.playTF = True
                print('ML playback paused')

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


        else:
            print('unknown playback option.')


        # except:
        #     QMessageBox.critical(self, "Error playing dataset", "Error playing dataset. \nMake sure a dataset is selected and try again.")
        pass

    def handleSingleImageProcessed(self,imgOut, imageNo):
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



    def disableAllButtons(self):
        pass

    def disablePlayPause(self):
        self.btnPlayPause.setEnabled(False)

    def enablePlayPause(self):
        self.btnPlayPause.setEnabled(True)

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
    sys.exit(app.exec())