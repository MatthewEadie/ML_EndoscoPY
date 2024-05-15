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

        #DISPLAY SIGNALS AND SLOTS
        self.checkBlueAutoContrast.clicked.connect(self.updateImageSettings)

        #SIGNALS AND SLOTS FOR CONTRAST SETTINGS
        self.sliderBlueMin.valueChanged.connect(self.updateImageSettings)
        self.sliderBlueMax.valueChanged.connect(self.updateImageSettings)



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
        self.grpBlueSliders = QGroupBox()
        self.grpBlueSlidersLayout = QHBoxLayout()
        self.grpBlueSliders.setLayout(self.grpBlueSlidersLayout)

        #Create two sliders (min/max value)
        self.sliderBlueMin = QSlider()
        self.sliderBlueMin.setMaximum(255)
        self.sliderBlueMin.setMinimum(0)
        self.sliderBlueMax = QSlider()
        self.sliderBlueMax.setMaximum(255)
        self.sliderBlueMax.setMinimum(0)
        self.sliderBlueMax.setValue(255)

        #Create label to display value of slider
        self.contrastLabelFont = QFont('Arial', 15)
        self.contrastLabelFont.setBold(True)
        self.lblBlueMin = QLabel('0')
        self.lblBlueMin.setFont(self.contrastLabelFont)
        self.lblBlueMax = QLabel('255')
        self.lblBlueMax.setFont(self.contrastLabelFont)

        #Add slider and labels to slider group
        self.grpBlueSlidersLayout.addWidget(self.lblBlueMin)
        self.grpBlueSlidersLayout.addWidget(self.sliderBlueMin)
        self.grpBlueSlidersLayout.addWidget(self.sliderBlueMax)
        self.grpBlueSlidersLayout.addWidget(self.lblBlueMax)
        
        #Create check box for auto contrast
        self.checkBlueAutoContrast = QCheckBox('Auto contrast')

        #Add sliders and auto contrast toggle to main group
        self.contrastTabLayout.addWidget(self.grpBlueSliders)
        self.contrastTabLayout.addWidget(self.checkBlueAutoContrast)

    def createCameraTab(self):

        # ---- TRIGGER MODE SETTINGS ---- # 
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


        # ---- EXPOSURE SETTINGS ---- #
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
        self.lblDatasetShape = QLabel('Selected Dataset:')
        self.txtDatasetShape = QLineEdit('')
        self.txtDatasetShape.setReadOnly(True)

        #Add label and txtbox to tab layout
        self.machineLearningTabLayout.addWidget(self.lblDatasetShape)
        self.machineLearningTabLayout.addWidget(self.txtDatasetShape)

        pass

    def createImageSlider(self):
        #h box
        self.groupImageSlider = QWidget()
        self.groupImageSliderLayout = QHBoxLayout()
        self.groupImageSlider.setLayout(self.groupImageSliderLayout)

        #button back image
        self.btnBackImageSlider = QPushButton('<')

        #slider
        self.imageSlider = QSlider(orientation=Qt.Horizontal)
        self.imageSlider.setMinimum(1)
        self.imageSlider.setMaximum(4000)

        #button forward image
        self.btnForwardImageSlider = QPushButton('>')

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

            #Update info box and ML tab
            self.okayInfoText('ML model loaded')
            self.txtChosenDataset.setText(MLDirectoryPath)
        except:
            #Display error message in info box
            self.errorInfoText('Error loading ML model')
        pass

    def newMLDatasetOpened(self, datasetPath):
        try:
            #Load dataset in ML pipeline
            self.datasetShape = self.MLPipeline.loadDataset(datasetPath)

            #Update info box and ML tab
            self.okayInfoText('Dataset loaded')
            self.txtChosenDataset.setText(datasetPath)

            #Display shape of dataset
            self.txtDatasetShape.setText(f'{self.datasetShape}')

            #Configure image selector to fit dataset
            self.configureImageSelector()
        except:
            #Display error message in info box
            self.errorInfoText('Error loading data')
        pass

    def configureImageSelector(self):
        self.imageSlider.setMaximum(self.datasetShape[0])
        self.txtRangeIndicator.setText(f'{0}/{self.datasetShape[0]}')

    def updateImageRangeCurrent(self):
        self.txtRangeIndicator.setText(f'{self.currentImageNo}/{self.datasetShape[0]}')
        self.imageSlider.setValue(self.currentImageNo)
        pass

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



    def handleSingleImageProcessed(self,imgOut, imageNo): #Duplicate function of updateSingleDisplay
        self.imageSingleScene.clear()
        self.imageSingleScene.addPixmap(imgOut.scaled(1080,720, aspectRatioMode=Qt.KeepAspectRatio))
        self.imageSingleScene.update()
        self.imageSingleDisplay.setScene(self.imageSingleScene)

        self.currentImageNo = imageNo
        self.updateImageRangeCurrent()

        pass

    def updateInfoLabel(self, newText):
        self.txtInfo.setText(f'{newText}')
        return
    
    def fpsCounter(self, fps):
        self.txtFPS.setText(f'FPS: {fps}')

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



    def errorInfoText(self, text):
        self.txtInfo.setStyleSheet("QLabel { background-color : red; color : blue; }")
        self.txtInfo.setText(text)

    def okayInfoText(self, text):
        self.txtInfo.setStyleSheet("QLabel { background-color : none; color : white; }")
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