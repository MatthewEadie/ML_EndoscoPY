import numpy as np

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class ImageRecorder(QObject):
    _imageBuffer = []

    mutex = QMutex()

    def recieveNewImage(self, newImage):
        self.mutex.lock()
        _image = newImage

        if len(self._imageBuffer) < 300:
            #Check to see if image buffer has reached 300 images
            self._imageBuffer.append(_image) #Append new image into buffer
        else:
            self._imageBuffer.pop(0) #Remove earliest image put into buffer
            self._imageBuffer.append(_image) # Append new image into buffer

        self.mutex.unlock()



    def saveImages(self):
        self._savingPath = ""
        pass