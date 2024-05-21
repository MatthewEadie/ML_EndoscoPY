"""
    Created by: Matthew Eadie
    Date: 10/01/22

    Work based off RAMS multiframe super resolution 
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import tensorflow as tf
from cv2 import imwrite
from math import floor
import time

from utils import commonFunctions as CF

from PyQt5.QtCore import *
from PyQt5.QtGui import QImage, QPixmap

class MLSettings:
    model_fp = ""
    dataset_path = ""

class machineLearningPipeline(QObject):
    updateImageML = pyqtSignal(QPixmap, int)

    channels = 0
    model_path = ""
    dataset_path = ""

    minContrast = 0
    maxContrast = 255

    stop_pressed = False #Default False


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

    def stopMLPlayback(self):
        self.stop_pressed = True

    def currentImageUpdated(self, imageNo):
        #Set thread current image value to new value
        self.currentImageNum = imageNo

        #Run ML and output new image
        self.singleImageML()


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



    def runML(self):
        self.stop_pressed = False

        while self.stop_pressed == False:

            #Get image from dataset
            outputImage = self.dataset[self.currentImageNum:self.currentImageNum+1,:,:,:]

            #Process image
            outputImage = self.processImage(outputImage)

            #Perform contrast adjustment
            outputImage = self.contrastAdjustment(outputImage)

            #Prepare image for display
            pix_output = self.prepareImageForDisplay(outputImage)

            #Emit image back to main page for display
            self.updateImageML.emit(pix_output, self.currentImageNum)

            time.sleep(1) # wait 1 second before looping

            #check if end of dataset has been reached
            if self.currentImageNum == self.dataset.shape[0]: # 0th items in dataset is number of images (eg 10,256,256,11 dataset has 10 images)
                self.currentImageNum = 0 #If end of dataset reached loop dataset
            else:
                self.currentImageNum += 1 #Else iterate to next image


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

