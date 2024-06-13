import numpy as np
from datetime import datetime

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class ImageRecorder(QObject):
    stackFull = pyqtSignal(np.ndarray)
    
    mutex = QMutex()

    recording = False

    def createDisplayBuffer(self,MLShape):
        #Read shape of input layer
        self.images = MLShape[0]
        self.height = MLShape[1] 
        self.width = MLShape[2]
        self.channels = MLShape[3]
        #Create empty array for storing images
        self._imageDisplayBuffer = np.zeros((1,self.height,self.width,self.channels))
        pass

    def addImageToDisplayStack(self, newImage, imageNumber):
        self.mutex.lock()
        _image = newImage/255 #needs to be reduced to between 0 and 1 before ML processing

        if imageNumber < self.channels:
            #Check to see if image buffer is full
            self._imageDisplayBuffer[0,:,:,imageNumber] = _image #Append new image into buffer
        else:
            #Use np.roll to move first image to last image
            self._imageDisplayBuffer = np.roll(self._imageDisplayBuffer, -1)
            #rewrite last image as new image
            self._imageDisplayBuffer[0,:,:,self.channels-1] = _image
            #Emit stack for processing
            self.stackFull.emit(self._imageDisplayBuffer)
            
            if self.recording == True:
                try:
                    #Send stack to save Buffer
                    self.addStackToSaveStack(self._imageDisplayBuffer, self.stackNo)
                    print('stack sent to save buffer')
                    #Increment stack number
                    self.stackNo += 1
                except:
                    pass

        self.mutex.unlock()
        pass

    def destroyDisplayStack(self):
        del self._imageDisplayBuffer

    def createSaveBuffer(self, MLShape):
        #Read shape of input layer
        self.images = MLShape[0]
        self.height = MLShape[1] 
        self.width = MLShape[2]
        self.channels = MLShape[3]
        #Create empty array for storing images
        print('create stackBuffer')
        self._stackBuffer = np.zeros((100,self.height,self.width,self.channels))
        print('buffer created')
        #Set stack number to 0
        self.stackNo = 0

    def addStackToSaveStack(self, newStack, stackNumber):
        _Stack = newStack

        if stackNumber < 100:
            #Check to see if image buffer has reached 300 images
            self._stackBuffer[stackNumber,:,:,:] = _Stack #Append new image into buffer
        else:
            #Use np.roll to move first image to last image
            self._stackBuffer = np.roll(self._stackBuffer, [0, 0, 0, -1], axis=(1, 0, 0, 0))
            #rewrite last image as new image
            self._stackBuffer[99,:,:,:] = _Stack


    def destroySaveStack(self):
        del self._stackBuffer

    def saveImages(self, savePath):
        self.mutex.lock()

        self._savingPath = savePath
        now = datetime.now()
        dateTime = now.strftime("%H-%M-%S_%d-%m-%Y")
        np.save(f'{self._savingPath}/{dateTime}.npy', self._stackBuffer)

        self.mutex.unlock()
        pass