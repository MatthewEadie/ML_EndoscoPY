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

class machineLearningPipeline(QObject):

    def loadModel(self, model_fp):
        #Copy file path to thread
        self.model_path = model_fp

        #Load trained model
        self.modelML = tf.keras.models.load_model(self.model_path, compile=False)
        self.modelML.compile(optimizer='adam',loss='mse')
        
        #Get shape of input layer
        self.firstLayerShape = self.modelML.layers[0].input_shape[0]
   

    def processStack(self, imageStack):
        X_pred = self.modelML(imageStack)

        pred_output = X_pred[0,:,:,0].numpy()
        pred_output *= 255
        pred_output[pred_output>255] = 255
        return pred_output