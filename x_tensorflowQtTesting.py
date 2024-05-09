import tensorflow as tf

import numpy as np
import matplotlib.pyplot as plt
import os
# from keras.saving import  #kersa now no longer dependant on tensorflow
from cv2 import imshow, imwrite, waitKey, cvtColor, COLOR_GRAY2RGB
from math import floor
import time


from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


#----------
# Settings
# channels = 11
# model_fp = "MFAE_Models/MFUNet_trained500_" + str(channels) 
# test_index = 3 #index of image to test model on
# path_datasets = "test images/image_stacks"
# save_path = "image_stacks/" + str(channels) 
#----------




# #Load testing datasets
# X_test = np.load(os.path.join(path_datasets, "X_test4D.npy")) #(32,256,256,4) Images to run through model
# Y_test = np.load(os.path.join(path_datasets, "Y_test4D.npy")) #(32,256,256,4) HR images for comparison

# #Load trained model
# MF_UNet = tf.keras.models.load_model(model_fp,compile=False)
# MF_UNet.compile(optimizer='adam',loss='mse')

# print(f"Shape of X_test: {X_test.shape}")
# print(f"Shape of Y_test: {Y_test.shape}")


# test_image = X_test[0:1]

# X_pred = MF_UNet(test_image)

# # fig, ax = plt.subplots(3)
# # ax[0].imshow(X_test[0,:,:,0])
# # ax[0].set_title('LR')

# # ax[1].imshow(X_pred[0,:,:,0])
# # ax[1].set_title('Prediction')

# # ax[2].imshow(Y_test[0])
# # ax[2].set_title('HR')

# # plt.show()

# plt.imshow(X_pred[0,:,:,0])
# plt.show

# imshow('Output',X_pred[0,:,:,0])
# waitKey(0)


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QGridLayout Example")
        self.setGeometry(50, 50, 800, 800)

        # Create a QGridLayout instance
        layout = QGridLayout()


        #----- GLOBAL VARIABLES -----
        channels = 11
        self.model_fp = "MFAE_Models/MFUNet_trained500_" + str(channels) 
        self.path_datasets = "test images/image_stacks"
        self.save_path = "image_stacks/" + str(channels) 


        self.imageSingleScene = QGraphicsScene()

        #Black large display
        self.displayImage = np.zeros((720,1080))
        height, width = self.displayImage.shape
        bytesPerLine = 3*width
        self.displayImage = QImage(self.displayImage.data, width, height, bytesPerLine, QImage.Format_Grayscale8)
        self.displayImage = QPixmap.fromImage(self.displayImage)

        self.createDisplayTab()
        layout.addWidget(self.displayTabs)
        self.setLayout(layout)


        ### PROGRAM START ###

        #Load ML model
        self.loadMLModel()

        #Load .npy dataset
        self.loadDataset()

        #Run ML and display
        self.runML()

    def createDisplayTab(self):
        self.displayTabs = QTabWidget()
        self.singleDisplay = QWidget()
        singleDisplayLayout = QGridLayout()
        self.singleDisplay.setLayout(singleDisplayLayout)

        self.imageSingleDisplay = QGraphicsView()
        self.imageSingleDisplay.setScene(self.imageSingleScene)

        singleDisplayLayout.addWidget(self.imageSingleDisplay,0,0)

        self.displayTabs.addTab(self.singleDisplay, "singleDisplay")

    def loadMLModel(self):
        # #Load trained model
        self.MF_UNet = tf.keras.models.load_model(self.model_fp,compile=False)
        self.MF_UNet.compile(optimizer='adam',loss='mse')

    def loadDataset(self):
        # #Load testing datasets
        self.X_test = np.load(os.path.join(self.path_datasets, "X_test4D.npy")) #(32,256,256,4) Images to run through model
        self.Y_test = np.load(os.path.join(self.path_datasets, "Y_test4D.npy")) #(32,256,256,4) HR images for comparison

    def runML(self):
        self.test_image = self.X_test[5:6]

        self.X_pred = self.MF_UNet(self.test_image)

        img_output = self.X_pred[0,:,:,0].numpy()
        img_output *= 255
        img_output[img_output>255] = 255


        # plt.imshow(img_output)
        # plt.show()

        # ----------- SOMETHING WRONG HERE -----------

        height,width = img_output.shape
        bytesPerLine = width            
        arrCombined = np.require(img_output, np.uint8, 'C')
        qImg = QImage(arrCombined.data, width, height, bytesPerLine, QImage.Format_Grayscale8)
        pix_output = QPixmap.fromImage(qImg)

        # ----------- SOMETHING WRONG HERE -----------

        self.updateSingleDisplay(pix_output)


    def updateSingleDisplay(self, imagePixmap):
        self.imageSingleScene.clear()
        self.imageSingleScene.addPixmap(imagePixmap.scaled(1080,720, aspectRatioMode=Qt.KeepAspectRatio))
        self.imageSingleScene.update()

        self.imageSingleDisplay.resetTransform()

        self.imageSingleDisplay.setScene(self.imageSingleScene)
        # self.imageSingleDisplay.setSceneRect(1080,720)
        # self.imageSingleDisplay.scale(256,256)
        # self.imageSingleDisplay.fitInView(self.imageScene.sceneRect(), Qt.KeepAspectRatio)
        self.imageSingleDisplay.setAlignment(Qt.AlignCenter)
        self.imageSingleDisplay.show()




if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)    

    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)

    app.setPalette(palette)
    window = Window()
    window.show()
    sys.exit(app.exec())