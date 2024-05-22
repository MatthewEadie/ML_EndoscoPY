import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import numpy as np

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QGridLayout Example")
        # self.setGeometry(50, 50, 1100, 750)


        # Create a QGridLayout instance
        layout = QGridLayout()

        #Create display image
        self.createDisplayImage()

        # Add widgets to the layout
        layout.addWidget(self.singleDisplay,0,0)

        # Set the layout on the application's window
        self.setLayout(layout)


        self.dataset = np.load('image_stacks\X_test4D.npy')

        #Get image from dataset
        outputImage = self.dataset[0:1,:,:,:]

        outputImage = self.singleFrameFromStack(outputImage)

        #Prepare image for display
        pix_output = self.prepareImageForDisplay(outputImage)

        self.updateDisplay(pix_output)


    def createDisplayImage(self):
        #Layout to contain image display
        self.singleDisplay = QWidget()
        singleDisplayLayout = QGridLayout()
        self.singleDisplay.setLayout(singleDisplayLayout)

        #A scene is required to display images
        self.imageSingleScene = QGraphicsScene()

        #Black pixmap for initial display
        self.displayImage = np.zeros((720,1080))
        height, width = self.displayImage.shape
        bytesPerLine = 3*width
        self.displayImage = QImage(self.displayImage.data, width, height, bytesPerLine, QImage.Format_Grayscale8)
        self.displayImage = QPixmap.fromImage(self.displayImage)
        self.imageSingleScene.addPixmap(self.displayImage)

        #Graphics view widget to display image
        self.imageSingleDisplay = QGraphicsView()
        self.imageSingleDisplay.setScene(self.imageSingleScene)

        #Add graphics view to layout
        singleDisplayLayout.addWidget(self.imageSingleDisplay,0,0)

    def singleFrameFromStack(self,imageStack):
        singleFrame = imageStack[0,:,:,0]
        return singleFrame*255

    def prepareImageForDisplay(self, outputImage):
        height,width = outputImage.shape
        bytesPerLine = width            
        arrCombined = np.require(outputImage, np.uint8, 'C')
        qImg = QImage(arrCombined.data, width, height, bytesPerLine, QImage.Format_Grayscale8)
        pixOutput = QPixmap.fromImage(qImg)

        return pixOutput
    
    def updateDisplay(self,imgOut):
        #Clear previous image from scene
        self.imageSingleScene.clear()
        #Add the pixmap of the new image to the scene
        self.imageSingleScene.addPixmap(imgOut.scaled(1080,720, aspectRatioMode=Qt.KeepAspectRatio))
        #Tell the scene to update
        self.imageSingleScene.update()
        #Set the display to the new scene
        self.imageSingleDisplay.setScene(self.imageSingleScene)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())