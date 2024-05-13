from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import PySpin

import matplotlib.pyplot as plt


import sys
import keyboard

import numpy as np

import time

import cv2


class CameraThread(QObject):
    imageAcquired = pyqtSignal(QPixmap)



    global continue_recording
    continue_recording = True

    def initialise(self):
        """
        Example entry point; notice the volume of data that the logging event handler
        prints out on debug despite the fact that very little really happens in this
        example. Because of this, it may be better to have the logger set to lower
        level in order to provide a more concise, focused log.

        :return: True if successful, False otherwise.
        :rtype: bool
        """
        result = True

        # Retrieve singleton reference to system object
        self.system = PySpin.System.GetInstance()

        # Get current library version
        version = self.system.GetLibraryVersion()
        print('Library version: %d.%d.%d.%d' % (version.major, version.minor, version.type, version.build))

        # Retrieve list of cameras from the system
        self.cam_list = self.system.GetCameras()

        num_cameras = self.cam_list.GetSize()

        print('Number of cameras detected: %d' % num_cameras)

        # Finish if there are no cameras
        if num_cameras == 0:

            # Clear camera list before releasing system
            self.cam_list.Clear()

            # Release system instance
            self.system.ReleaseInstance()

            print('Not enough cameras!')
            input('Done! Press Enter to exit...')
            return False
        
        return result
    
    def exit(self):
        self.captureStop = True


    def endAcquisition(self):
        # Release reference to camera
        # NOTE: Unlike the C++ examples, we cannot rely on pointer objects being automatically
        # cleaned up when going out of scope.
        # The usage of del is preferred to assigning the variable to None.
        del self.cam

        # Clear camera list before releasing system
        self.cam_list.Clear()

        # Release system instance
        self.system.ReleaseInstance()

        print('Acquisition ended.')

            

    def acquire_and_display_images(self, nodemap, nodemap_tldevice):
        """
        This function continuously acquires images from a device and display them in a GUI.

        :param cam: Camera to acquire images from.
        :param nodemap: Device nodemap.
        :param nodemap_tldevice: Transport layer device nodemap.
        :type cam: CameraPtr
        :type nodemap: INodeMap
        :type nodemap_tldevice: INodeMap
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        global continue_recording
        continue_recording = True

        sNodemap = self.cam.GetTLStreamNodeMap()

        # Change bufferhandling mode to NewestOnly
        node_bufferhandling_mode = PySpin.CEnumerationPtr(sNodemap.GetNode('StreamBufferHandlingMode'))
        if not PySpin.IsReadable(node_bufferhandling_mode) or not PySpin.IsWritable(node_bufferhandling_mode):
            print('Unable to set stream buffer handling mode.. Aborting...')
            return False

        # Retrieve entry node from enumeration node
        node_newestonly = node_bufferhandling_mode.GetEntryByName('NewestOnly')
        if not PySpin.IsReadable(node_newestonly):
            print('Unable to set stream buffer handling mode.. Aborting...')
            return False

        # Retrieve integer value from entry node
        node_newestonly_mode = node_newestonly.GetValue()

        # Set integer value from entry node as new value of enumeration node
        node_bufferhandling_mode.SetIntValue(node_newestonly_mode)

        print('*** IMAGE ACQUISITION ***\n')
        try:
            node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
            if not PySpin.IsReadable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
                print('Unable to set acquisition mode to continuous (enum retrieval). Aborting...')
                return False

            # Retrieve entry node from enumeration node
            node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
            if not PySpin.IsReadable(node_acquisition_mode_continuous):
                print('Unable to set acquisition mode to continuous (entry retrieval). Aborting...')
                return False

            # Retrieve integer value from entry node
            acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

            # Set integer value from entry node as new value of enumeration node
            node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

            print('Acquisition mode set to continuous...')

            #  Begin acquiring images
            #
            #  *** NOTES ***
            #  What happens when the camera begins acquiring images depends on the
            #  acquisition mode. Single frame captures only a single image, multi
            #  frame catures a set number of images, and continuous captures a
            #  continuous stream of images.
            #
            #  *** LATER ***
            #  Image acquisition must be ended when no more images are needed.
            self.cam.BeginAcquisition()

            print('Acquiring images...')

            #  Retrieve device serial number for filename
            #
            #  *** NOTES ***
            #  The device serial number is retrieved in order to keep cameras from
            #  overwriting one another. Grabbing image IDs could also accomplish
            #  this.
            device_serial_number = ''
            node_device_serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode('DeviceSerialNumber'))
            if PySpin.IsReadable(node_device_serial_number):
                device_serial_number = node_device_serial_number.GetValue()
                print('Device serial number retrieved as %s...' % device_serial_number)

            # Close program
            print('Press enter to close the program..')

            # # Figure(1) is default so you can omit this line. Figure(0) will create a new window every time program hits this line
            fig = plt.figure(1)

            # # Close the GUI when close event happens
            # fig.canvas.mpl_connect('close_event', self.handle_close)

            print(f'Recording: {continue_recording}')

            init = 1

            # Retrieve and display images
            while(continue_recording):
                try:

                    #  Retrieve next received image
                    #
                    #  *** NOTES ***
                    #  Capturing an image houses images on the camera buffer. Trying
                    #  to capture an image that does not exist will hang the camera.
                    #
                    #  *** LATER ***
                    #  Once an image from the buffer is saved and/or no longer
                    #  needed, the image must be released in order to keep the
                    #  buffer from filling up.
                    
                    image_result = self.cam.GetNextImage(100)

                    #  Ensure image completion
                    if image_result.IsIncomplete():
                        print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

                    else:  

                        print('Image captured')                  

                        # Getting the image data as a numpy array
                        image_data = image_result.GetNDArray()

                        # plt.imshow(image_data, cmap='gray')
                        # plt.pause(0.001)
                        # plt.clf()

                        # time.sleep(5)

                        # if init==1:
                        #     time.sleep(5)
                        #     init=0


                        height,width = image_data.shape
                        imgOut = np.zeros((height,width,3))
                        imgOut[:,:,0] = image_data
                        bytesPerLine = 3*width            
                        arrCombined = np.require(imgOut, np.uint8, 'C')
                        qImg = QImage(arrCombined.data, width, height, bytesPerLine, QImage.Format_RGB888)
                        pixmap = QPixmap.fromImage(qImg)


                        # Draws an image on the current figure
                        self.imageAcquired.emit(pixmap.scaled(720,512, aspectRatioMode=Qt.KeepAspectRatio))


                        print('Image emitted')

                        # if init==1:
                        #     time.sleep(10)
                        #     init=0

                        # print('time passed')


                        # Interval in plt.pause(interval) determines how fast the images are displayed in a GUI
                        # Interval is in seconds.
                        # time.sleep(0.01)

                        # Clear current reference of a figure. This will improve display speed significantly
                        
                        # If user presses enter, close the program
                        if self.captureStop==True:
                            print('Program is closing...')
                            
                            # Close figure
                            plt.close('all')   

                            # input('Done! Press Enter to exit...')
                            continue_recording=False

                    #  Release image
                    #
                    #  *** NOTES ***
                    #  Images retrieved directly from the camera (i.e. non-converted
                    #  images) need to be released in order to keep from filling the
                    #  buffer.
                    image_result.Release()

                    print('image released')


                except PySpin.SpinnakerException as ex:
                    print('Error: %s' % ex)
                    return False
                
            #  End acquisition
            #
            #  *** NOTES ***
            #  Ending acquisition appropriately helps ensure that devices clean up
            #  properly and do not need to be power-cycled to maintain integrity.
            self.cam.EndAcquisition()
            
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False

        return True

    @pyqtSlot()
    def run_single_camera(self):
        """
        This function acts as the body of the example; please see NodeMapInfo example
        for more in-depth comments on setting up cameras.

        :param cam: Camera to run on.
        :type cam: CameraPtr
        :return: True if successful, False otherwise.
        :rtype: bool
        """

        self.cam = self.cam_list[0]

        self.captureStop = False

        try:
            result = True

            nodemap_tldevice = self.cam.GetTLDeviceNodeMap()

            # Initialize camera
            self.cam.Init()

            # Retrieve GenICam nodemap
            nodemap = self.cam.GetNodeMap()

            # Acquire images
            result &= self.acquire_and_display_images(nodemap, nodemap_tldevice)

            # # Deinitialize camera
            # self.cam.DeInit()

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False

        # try:
        #     self.endAcquisition()

        # except PySpin.SpinnakerException as ex:
        #     print('Error: %s' % ex)
        #     result = False

        print('Program Exited')
        return result


class MainWindow(QWidget):
    beginCapture = pyqtSignal()

    def __init__(self):
        super().__init__()

        
        self.displayImage = QPixmap('./images/MTF graph.png')

        self.setWindowTitle("My App")

        self.setGeometry(100, 100, 800, 800)

        self.l = QGridLayout()
        self.setLayout(self.l)

        self.display = QLabel('image')
        self.display.setPixmap(self.displayImage.scaled(1080,720, aspectRatioMode=Qt.KeepAspectRatio))
        self.l.addWidget(self.display,0,0,3,1)

        self.btnInitCam = QPushButton('Initialise')
        self.btnInitCam.clicked.connect(self.initCamera)
        self.l.addWidget(self.btnInitCam,0,1)

        self.btnPlay = QPushButton('Play')
        self.btnPlay.clicked.connect(self.playPressed)
        self.l.addWidget(self.btnPlay,1,1)

        self.btnStop = QPushButton('Stop')
        self.btnStop.clicked.connect(self.stopPressed)
        self.l.addWidget(self.btnStop,2,1)

        self.cameraFunctions = CameraThread()
        self.cameraThread = QThread()

        self.cameraFunctions.moveToThread(self.cameraThread)

        self.cameraThread.start()

        self.cameraFunctions.initialise()

        # self.btnInitCam.setEnabled(False)
        # self.btnPlay.setEnabled(True)
        # self.btnStop.setEnabled(False)

        #SLOTS
        self.beginCapture.connect(self.cameraFunctions.run_single_camera)
        self.cameraFunctions.imageAcquired.connect(self.updateDisplay)





    def initCamera(self):
        # self.btnInitCam.setEnabled(False)
        # self.btnPlay.setEnabled(True)
        # self.btnStop.setEnabled(False)

        self.cameraFunctions.initialise()


    def playPressed(self):
        # self.btnInitCam.setEnabled(False)
        # self.btnPlay.setEnabled(False)
        # self.btnStop.setEnabled(True)

        self.beginCapture.emit()
        return
    
    def stopPressed(self):
        # self.btnInitCam.setEnabled(True)
        # self.btnPlay.setEnabled(False)
        # self.btnStop.setEnabled(False)

        self.cameraFunctions.exit()
        # self.cameraFunctions.terminate()
        return
    
    def updateDisplay(self, imagePixmap):
        self.display.setPixmap(imagePixmap)
        print('image updated')

 



       





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