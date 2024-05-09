import sys
from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui 
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from scipy import signal
import numpy as np


class PlotViewer(QWidget):

    doubleClickAction = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(PlotViewer, self).__init__(parent)

        self.figure = plt.figure(figsize=(5, 5))
        self.ax = self.figure.add_subplot(111)
        self.figureCanvas = FigureCanvas(self.figure)
        # self.navigationToolbar = NavigationToolbar(self.figureCanvas, self)

        # create main layout
        layout = QGridLayout()
        # layout.addWidget(self.navigationToolbar)
        

        self.blueHTime = QDoubleSpinBox()
        self.blueHTime.setDecimals(3)
        self.blueHTime.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.blueHTime.setValue(0.5)
        self.blueHTime.valueChanged.connect(self.updateGraph)

        self.blueLTime = QDoubleSpinBox()
        self.blueLTime.setDecimals(3)
        self.blueLTime.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.blueLTime.setValue(0.5)
        self.blueLTime.valueChanged.connect(self.updateGraph)

        self.blueDelay = QDoubleSpinBox()
        self.blueDelay.setDecimals(3)
        self.blueDelay.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.blueDelay.setValue(0)
        self.blueDelay.valueChanged.connect(self.updateGraph)

        layout.addWidget(self.blueHTime,0,0)
        layout.addWidget(self.blueLTime,0,1)
        layout.addWidget(self.blueDelay,0,2)

        layout.addWidget(self.figureCanvas,2,0,3,3)
        self.setLayout(layout)

        self.updateGraph()

        # self.blueLTime = QtWidgets.QSpinBox()
        # self.bluedelay = QtWidgets.QSpinBox()

    def updateGraph(self):
        self.ax.clear()

        t = np.linspace(0,1,500)

        print('graph updated')

        highTime = self.blueHTime.value()
        lowTime = self.blueLTime.value()
        delay = self.blueDelay.value()
        wavelen = (2*np.pi)#*(highTime+lowTime)
        dutyP = 1/((highTime+lowTime)/highTime)
        noWaves = 1
        offset = wavelen*delay

        sig1 = signal.square((wavelen*noWaves*t)-offset,duty=dutyP)

        highTime = 0.5
        lowTime = 0.5
        delay = 0
        wavelen = 2*np.pi
        noWaves = 1/(highTime+lowTime)
        offset = wavelen*delay

        sig2 = signal.square((wavelen*noWaves*t)-offset)

        # create an axis
        # x = range(0, 10, 0.1)
        # y = range(0, 20, 2)
        self.ax.plot(t, sig1, label='sig 1')
        self.ax.plot(t, sig2, label='sig 2')
        self.ax.legend()


        # show canvas
        self.figureCanvas.show()
        self.figureCanvas.draw()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    widget = PlotViewer()
    widget.show()
    app.exec_()