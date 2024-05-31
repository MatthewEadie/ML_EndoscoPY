import numpy as np
from datetime import datetime

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class ImageRecorder(QObject):
    stackFull = pyqtSignal(np.ndarray)
    
    mutex = QMutex()

    def createDisplayStack(self,MLShape):
        #Read shape of input layer
        images, height, width, self.channels = MLShape.shape
        #Create empty array for storing images
        self._imageDisplayBuffer = np.zeros((height,width,self.channels))
        pass

    def addImageToDisplayStack(self, newImage, imageNumber):
        self.mutex.lock()
        _image = newImage

        if imageNumber < self.channels:
            #Check to see if image buffer is full
            self._imageDisplayBuffer[:,:,imageNumber] = _image #Append new image into buffer
        else:
            #Use np.roll to move first image to last image
            self._imageDisplayBuffer = np.roll(self._imageDisplayBuffer, -1)
            #rewrite last image as new image
            self._imageDisplayBuffer[:,:,self.channels] = _image
            #Emit stack for processing
            self.stackFull.emit(self._imageDisplayBuffer)

        self.mutex.unlock()


        pass

    def createSaveBuffer(self,MLShape):
        #Read shape of input layer
        images, height, width, channels = MLShape.shape
        #Create empty array for storing images
        self._stackBuffer = np.zeros((100,height,width,channels))


    def addStackToSaveStack(self, newImage, stackNumber):
        self.mutex.lock()
        _image = newImage

        if stackNumber < 100:
            #Check to see if image buffer has reached 300 images
            self._stackBuffer[stackNumber,:,:,:] = _image #Append new image into buffer
        else:
            #Use np.roll to move first image to last image
            self._stackBuffer = np.roll(self._stackBuffer, [0, 0, 0, -1], axis=(1, 0, 0, 0))
            #rewrite last image as new image
            self._stackBuffer[99,:,:,:] = _image

        self.mutex.unlock()


    def saveImages(self, savePath):
        self.mutex.lock()

        self._savingPath = savePath
        now = datetime.now()
        dateTime = now.strftime("%H-%M-%S_%d-%m-%Y")
        np.save(f'{self._savingPath}+{dateTime}.npy', self._stackBuffer)

        self.mutex.unlock()
        pass