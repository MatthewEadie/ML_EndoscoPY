from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


import pyqtgraph as pg

import numpy as np

import cv2


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        self.setGeometry(100, 100, 800, 800)

        self.l = QGridLayout()
        self.setLayout(self.l)


        image = cv2.imread("./test images/midImages/Calibration Data/Exposure_25ms/lightfieldMid.tif",0)

        self.im1 = pg.ImageView()
        self.im1.setFixedWidth(1200)
        self.im1.setImage(image)
        self.im1.getView().setMenuEnabled(False)
        self.l.addWidget(self.im1,0,0,5,5)

        self.im2 = pg.ImageView()
        self.im2.setFixedWidth(1200)
        self.im2.setImage(image)
        self.im2.getView().setMenuEnabled(False)
        self.l.addWidget(self.im2,0,6,5,5)

        # self.vb = pg.PlotItem()
        # self.vb.addItem(self.roi)
        # self.vb.setImage(image)

        # self.l.addWidget(self.vb,6,0)
 



        # Set the central widget of the Window.
        button = QPushButton("Press Me!")
        self.l.addWidget(button)





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
    window = MainWindow()
    window.show()
    sys.exit(app.exec())