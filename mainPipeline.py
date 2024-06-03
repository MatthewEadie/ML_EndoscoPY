import numpy as np
import matplotlib.pyplot as plt
import os
import tensorflow as tf
from cv2 import imwrite
from math import floor
import time

from utils import commonFunctions as CF


from cameraSettings import CameraPipeline
from imageRecorder import ImageRecorder
from MLPipeline import machineLearningPipeline


from PyQt5.QtCore import *
from PyQt5.QtGui import QImage, QPixmap



class mainPipeline(QObject):
    updateImagePlayback = pyqtSignal(QPixmap, int)
    updateImageAcquisition = pyqtSignal(QPixmap)

    channels = 0
    model_path = ""
    dataset_path = ""

    minContrast = 0
    maxContrast = 255

    stop_pressed = False #Default False
    TFML = False #Machine learning off by default



    # ---- MACHINE LEARNING FUNCTIONS ---- #
    def createMLThread(self):
        # MACHINE LEARNING THREAD #
        self.machineLearningFunctions = machineLearningPipeline()
        self.machineLearningThread = QThread()
        self.machineLearningFunctions.moveToThread(self.machineLearningThread)
        self.machineLearningThread.start()
        pass

    def loadMLModel(self, modelFilepath):
        #Send model filepath to ML pipeline for loading
        self.machineLearningFunctions.loadModel(modelFilepath)
        #Get shape of input layer for display
        self.firstLayerShape = self.machineLearningFunctions.firstLayerShape





# ---- PLAYBACK FUNCTIONS ---- #
    def singleImagePlayback(self):
        outputImage = self.dataset[self.currentImageNum:self.currentImageNum+1,:,:,:]
        
        #Process image
        if self.TFML == True:
            outputImage = self.machineLearningFunctions.processStack(outputImage)
        else:
            #Need to put 4D image into 1D array
            outputImage = self.singleFrameFromStack(outputImage)
            pass
        
        #Perform contrast adjustment
        outputImage = self.contrastAdjustment(outputImage)

        #Prepare image for display
        pixOutputImage = self.prepareImageForDisplay(outputImage)
        
        #Emit image back to main page for display
        self.updateImagePlayback.emit(pixOutputImage, self.currentImageNum)

    def runPlayback(self):
        self.stop_pressed = False

        while self.stop_pressed == False:

            #Get image from dataset
            outputImage = self.dataset[self.currentImageNum:self.currentImageNum+1,:,:,:]

            #Process image
            if self.TFML == True:
                outputImage = self.machineLearningFunctions.processStack(outputImage)
            else:
                #Need to put 4D image into 1D array
                outputImage = self.singleFrameFromStack(outputImage)
                pass

            #Perform contrast adjustment
            outputImage = self.contrastAdjustment(outputImage)

            #Prepare image for display
            pix_output = self.prepareImageForDisplay(outputImage)

            #Emit image back to main page for display
            self.updateImagePlayback.emit(pix_output, self.currentImageNum)

            time.sleep(1) # wait 1 second before looping

            #check if end of dataset has been reached
            if self.currentImageNum == self.dataset.shape[0]: # 0th items in dataset is number of images (eg 10,256,256,11 dataset has 10 images)
                self.currentImageNum = 0 #If end of dataset reached loop dataset
            else:
                self.currentImageNum += 1 #Else iterate to next image

    def stopPlayback(self):
        self.stop_pressed = True



# ---- CAMERA FUNCTIONS ---- #
    def initaliseCamera(self):
        tfCameraInitalised = self.cameraFunctions.initialiseCamera()
        return tfCameraInitalised

    def runAcquisition(self):
        #Reset image number to 0
        self.currentImageNum = 0

        #Tell camera to beging acquiring
        self.cameraFunctions.run_single_camera()

        pass

    def stopAcquisition(self):
        #Tell camera to stop acquiring
        self.cameraFunctions.stopCapture()
        pass

    def processCameraImage(self, cameraImage, imageNumber):
        #When image recieved from camera:
        
        if self.TFML:
            #If ML on send image to stack
            self.sendImageToStack(cameraImage, imageNumber)
        else:
            #If ML off - Process image
            pix_output = self.singleImageFromCamera(cameraImage)
        
            # Draws an image on the current figure
            self.updateImageAcquisition.emit(pix_output)

        pass



# ---- GENERAL FUNCTIONS ---- #
    def toggleML(self, tfPerformML):
        #Update local variable to check if performing ML
        self.TFML = tfPerformML

    def contrastChanged(self, minCont, maxCont):
        #Update thread contrast values
        self.minContrast = minCont
        self.maxContrast = maxCont
        #Run single image incase playback is paused
        if self.stop_pressed:
            self.singleImageML()
     
    def loadDataset(self, dataset_fp):
        #Copy file path to thread
        self.dataset_path = dataset_fp   

        #Load the dataset
        self.dataset = np.load(self.dataset_path)

        #Set current image number to 0
        self.currentImageNum = 0

        #Return the shape of the dataset for UI features
        return self.dataset.shape

    def currentImageUpdated(self, imageNo):
        #Set thread current image value to new value
        self.currentImageNum = imageNo

        #Run ML and output new image
        self.singleImagePlayback()

    def contrastAdjustment(self, outputImage):
        outputImage = CF.AdjustContrastImage(outputImage, self.minContrast, self.maxContrast)
        return outputImage

    def prepareImageForDisplay(self, outputImage):
        height,width = outputImage.shape
        bytesPerLine = width            
        arrCombined = np.require(outputImage, np.uint8, 'C')
        qImg = QImage(arrCombined.data, width, height, bytesPerLine, QImage.Format_Grayscale8)
        pixOutput = QPixmap.fromImage(qImg)

        return pixOutput

    def singleFrameFromStack(self, imageStack):
        #Get the first image in the stack with only the first channel
        singleFrame = imageStack[0,:,:,0]
        #Multiply by 255 to get values between 1 and 256 instead of 0 and 1
        singleFrame *= 255
        return singleFrame



    def singleImageFromCamera(self,cameraImage):
        height,width = cameraImage.shape
        imgOut = np.zeros((height,width,3))
        #Format is RGB
        imgOut[:,:,0] = cameraImage
        imgOut[:,:,1] = cameraImage
        imgOut[:,:,2] = cameraImage

        bytesPerLine = 3*width            
        arrCombined = np.require(imgOut, np.uint8, 'C')
        qImg = QImage(arrCombined.data, width, height, bytesPerLine, QImage.Format_RGB888)
        pix_output = QPixmap.fromImage(qImg)
        return pix_output
    
    def createCameraThread(self):
        # CAMERA THREAD #
        self.cameraFunctions = CameraPipeline()
        self.cameraThread = QThread()
        self.cameraFunctions.moveToThread(self.cameraThread)
        self.cameraThread.start()

        #Slot to recieve image from camera
        self.cameraFunctions.imageAcquired.connect(self.processCameraImage)

        # RECORDER THREAD #
        self.recorderFunctions = ImageRecorder()
        self.recorderThread = QThread()
        self.recorderFunctions.moveToThread(self.recorderThread)
        self.recorderThread.start()

        #Slot to recieve full stack from recorder
        self.recorderFunctions.stackFull.connect(self.machineLearningFunctions.processStack)

    def stopCameraThread(self):
        #Exit camera thread
        self.cameraThread.exit() 

        #Exit recorder thread
        self.recorderThread.exit()
        pass

    def setCameraSettings(self, MLInputShape, exposureTime):
        #Copy ML shape for buffer shape
        self.mlShape = MLInputShape
        #Copy exposure time for initial setup
        self.exposureTime = exposureTime

    def createSaveStack(self):
        #Pass mlshape to image recorder class
        self.recorderFunctions.createSaveBuffer(self.mlShape)

    def sendImageToStack(self, image, imageNum):
        self.recorderFunctions.addImageToDisplayStack(image, imageNum)

    def setSaveLocation(self, newSavePath):
        #Update local path to new path
        self.savePath = newSavePath

    def saveImageStack(self):
        #Tell image recorder thread to save stack
        self.recorderFunctions.saveImages(self.savePath)
        pass
