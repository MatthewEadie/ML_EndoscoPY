import numpy as np
from datetime import datetime

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class ImageRecorder(QObject):
    
    mutex = QMutex()

    def createBuffer(self,MLShape):
        #Read shape of input layer
        images, height, width, channels = MLShape.shape
        #Create empty array for storing images
        self._imageBuffer = np.zeros((100,height,width,channels))


    def addImageToStack(self, newImage, imageNumber):
        self.mutex.lock()
        _image = newImage

        if imageNumber < 100:
            #Check to see if image buffer has reached 300 images
            self._imageBuffer[imageNumber,:,:,:] = _image #Append new image into buffer
        else:
            #Use np.roll to move first image to last image
            self._imageBuffer = np.roll(self._imageBuffer, [0, 0, 0, -1], axis=(1, 0, 0, 0))
            #rewrite last image as new image
            self._imageBuffer[99,:,:,:] = _image

        self.mutex.unlock()



    def saveImages(self, savePath):
        self._savingPath = savePath
        now = datetime.now()
        dateTime = now.strftime("%H-%M-%S_%d-%m-%Y")
        np.save(f'{self._savingPath}+{dateTime}.npy', self._imageBuffer)
        pass