from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


"""Example of CO pulse time operation."""
import time

import nidaqmx
from nidaqmx.constants import AcquisitionType
from nidaqmx.types import CtrTime


# with nidaqmx.Task() as task:
#     task.co_channels.add_co_pulse_chan_time("cDAQ_VER/ctr0",initial_delay=0.0, low_time=0.5, high_time=0.5) #I/O channel 0 
#     task.co_channels.add_co_pulse_chan_time("cDAQ_VER/ctr1",initial_delay=0.0, low_time=0.5, high_time=0.5) #I/O channel 3
#     # task.co_channels.add_co_pulse_chan_time("cDAQ_VER/ctr2",initial_delay=0.0, low_time=0.5, high_time=0.5) #I/O channel 1 
#     # task.co_channels.add_co_pulse_chan_time("cDAQ_VER/ctr3",initial_delay=0.1, low_time=0.15, high_time=0.05) I/O channel 2
#     # task.timing.cfg_implicit_timing(sample_mode=AcquisitionType.CONTINUOUS)
#     task.timing.cfg_implicit_timing(sample_mode=AcquisitionType.FINITE, samps_per_chan=10)
#     task.start()

#     while(not(task.is_task_done())):
#             task.is_task_done()


class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("My App")

        self.setGeometry(100, 100, 800, 500)

        self.l = QGridLayout()

        self.button = QPushButton("Set trigger")
        self.button.clicked.connect(self.setTrigger)

        self.buttonStop = QPushButton("Run trigger")
        self.buttonStop.clicked.connect(self.runTrigger)


        self.l.addWidget(self.button,0,0)
        self.l.addWidget(self.buttonStop,1,0)

        self.setLayout(self.l)

    def setTrigger(self):
        self.task = nidaqmx.Task()
        
        self.task.co_channels.add_co_pulse_chan_time("cDAQ_VER/ctr0",initial_delay=0.0, low_time=0.5, high_time=0.5) #I/O channel 0 
        self.task.co_channels.add_co_pulse_chan_time("cDAQ_VER/ctr1",initial_delay=0.0, low_time=0.5, high_time=0.5) #I/O channel 3
        # task.co_channels.add_co_pulse_chan_time("cDAQ_VER/ctr2",initial_delay=0.0, low_time=0.5, high_time=0.5) #I/O channel 1 
        # task.co_channels.add_co_pulse_chan_time("cDAQ_VER/ctr3",initial_delay=0.1, low_time=0.15, high_time=0.05) I/O channel 2
        # task.timing.cfg_implicit_timing(sample_mode=AcquisitionType.CONTINUOUS)
        self.task.timing.cfg_implicit_timing(sample_mode=AcquisitionType.FINITE, samps_per_chan=10)

        print('trigger set')
            

    def runTrigger(self):
        print('starting trigger')
        self.task.start()

        while(not(self.task.is_task_done())):
                self.task.is_task_done()
        




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
