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

from PyQt5.QtCore import *
from PyQt5.QtGui import QImage, QPixmap

class MLSettings:
    model_fp = ""
    dataset_path = ""

class machineLearningPipeline(QObject):
    updateImageML = pyqtSignal(QPixmap)

    channels = 0
    model_path = ""
    dataset_path = ""


    def loadModel(self, model_fp):
        #Load trained model
        self.model_path = model_fp

        try:
            self.modelML = tf.keras.models.load_model(self.model_path, compile=False)
            self.modelML.compile(optimizer='adam',loss='mse')
            return 'Model loaded'
        
        except:
            return 'Error loading ML model'
        


    def loadDataset(self, dataset_fp):
        self.dataset_path = dataset_fp
        self.dataset = np.load(self.dataset_path)

        print('dataset loaded')

        # try:
        #     self.dataset = np.load(self.dataset_path)
        # except:
        #     print('Error loading data')

    def stopMLPlayback(self):
        self.stop_pressed = True

    @pyqtSlot()
    def runML(self):

        print('running ML reconstruction')

        imageNum = 0
        self.stop_pressed = False

        while self.stop_pressed == False:

            X_pred = self.modelML(self.dataset[imageNum:imageNum+1,:,:,:])

            #emit X_Pred for display on screen
            pred_output = X_pred[0,:,:,0].numpy()
            pred_output *= 255
            pred_output[pred_output>255] = 255


            height,width = pred_output.shape
            bytesPerLine = width            
            arrCombined = np.require(pred_output, np.uint8, 'C')
            qImg = QImage(arrCombined.data, width, height, bytesPerLine, QImage.Format_Grayscale8)
            pix_output = QPixmap.fromImage(qImg)

            self.updateImageML.emit(pix_output)

            time.sleep(1) # wait 1 second before looping

            #check if end of dataset has been reached
            if imageNum == self.dataset.shape[0]: # 0th items in dataset is number of images (eg 10,256,256,11 dataset has 10 images)
                imageNum = 0 #If end of dataset reached loop dataset
            else:
                imageNum += 1 #Else iterate to next image



