import numpy as np
import matplotlib.pyplot as plt
import os
import tensorflow as tf
from cv2 import imwrite
from math import floor
import time

from utils import commonFunctions as CF


from cameraSettings import CameraThread
from imageRecorder import ImageRecorder


from PyQt5.QtCore import *
from PyQt5.QtGui import QImage, QPixmap

class MLSettings:
    model_fp = ""
    dataset_path = ""

class machineLearningPipeline(QObject):
    updateImagePlayback = pyqtSignal(QPixmap, int)
    updateImageAcquisition = pyqtSignal(QPixmap)

    channels = 0
    model_path = ""
    dataset_path = ""

    minContrast = 0
    maxContrast = 255

    stop_pressed = False #Default False
    TFML = True #Machine learning no by default

    def createCameraThread(self):
        # CAMERA THREAD #
        self.cameraFunctions = CameraThread()
        self.cameraThread = QThread()
        self.cameraFunctions.moveToThread(self.cameraThread)

        #Slot to recieve image from camera
        self.cameraFunctions.imageAcquired.connect(self.processCameraImage)

        # RECORDER THREAD #
        self.recorderFunctions = ImageRecorder()
        self.recorderThread = QThread()
        self.recorderFunctions.moveToThread(self.recorderThread)

    def stopCameraThread(self):
        #Exit camera thread
        self.cameraThread.exit() 

        #Exit recorder thread
        self.recorderThread.exit()
        pass

    def initaliseCamera(self):
        tfCameraInitalised = self.cameraFunctions.initialiseCamera()
        return tfCameraInitalised



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

    def loadModel(self, model_fp):
        #Copy file path to thread
        self.model_path = model_fp

        #Load trained model
        self.modelML = tf.keras.models.load_model(self.model_path, compile=False)
        self.modelML.compile(optimizer='adam',loss='mse')
        
        #Get shape of input layer
        self.firstLayerShape = self.modelML.layers[0].input_shape[0]
        
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
        self.singleImageML()



# ---- PLAYBACK FUNCTIONS ---- #

    def singleImageML(self):
        outputImage = self.dataset[self.currentImageNum:self.currentImageNum+1,:,:,:]
        
        #Process image
        outputImage = self.processImage(outputImage)

        #Perform contrast adjustment
        outputImage = self.contrastAdjustment(outputImage)

        #Prepare image for display
        pixOutputImage = self.prepareImageForDisplay(outputImage)
        
        #Emit image back to main page for display
        self.updateImageML.emit(pixOutputImage, self.currentImageNum)

    def runMLPlayback(self):
        self.stop_pressed = False

        while self.stop_pressed == False:

            #Get image from dataset
            outputImage = self.dataset[self.currentImageNum:self.currentImageNum+1,:,:,:]

            #Process image
            if self.TFML == True:
                outputImage = self.processImage(outputImage)
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

    def stopMLPlayback(self):
        self.stop_pressed = True



# ---- CAMERA FUNCTIONS ---- #

    def runMLAcquisition(self):
        #Reset image number to 0
        self.currentImageNum = 0

        #Tell camera to beging acquiring
        self.cameraFunctions.run_single_camera()

        pass

    def stopMLAcquisition(self):
        #Tell camera to stop acquiring
        self.cameraFunctions.stopCapture()
        pass

    def setCameraSettings(self, MLInputShape, exposureTime):
        #Copy ML shape for buffer shape
        self.mlShape = MLInputShape
        #Copy exposure time for initial setup
        self.exposureTime = exposureTime

    def createSaveStack(self):
        #Pass mlshape to image recorder class
        self.recorderFunctions.createBuffer(self.mlShape)

    def sendImageToStack(self, image, imageNum):
        self.recorderFunctions.addImageToStack(image, imageNum)

    def setSaveLocation(self, savePath):
        #Update local path to new path
        self.savePath = savePath

    def saveImageStack(self):
        #Tell image recorder thread to save stack
        self.recorderFunctions.saveImages(self.savePath)
        pass

    def processCameraImage(self, cameraImage):
        #When image recieved from camera:
        

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


        # Draws an image on the current figure
        self.updateImageAcquisition.emit(pix_output)

        #Check if image should be written to stack
        
        #Iterate image number
        self.currentImageNum += 1
        pass



# ---- GENERAL FUNCTIONS ---- #

    def processImage(self, image):
        X_pred = self.modelML(image)

        pred_output = X_pred[0,:,:,0].numpy()
        pred_output *= 255
        pred_output[pred_output>255] = 255
        return pred_output
    
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

