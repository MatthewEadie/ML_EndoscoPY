from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import PySpin
import matplotlib.pyplot as plt
import sys
import keyboard
import numpy as np
import time





class CameraPipeline(QObject):
    imageAcquired = pyqtSignal(np.ndarray, int)
    updateFPS = pyqtSignal(int)


    global continue_recording
    continue_recording = True



    def initialiseCamera(self):
        # try:
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

                return False
            
            self.cam = self.cam_list[0]

            self.nodemap_tldevice = self.cam.GetTLDeviceNodeMap()

            # Initialize camera
            print('Init camera')
            self.cam.Init()

            # Retrieve GenICam nodemap
            print('get node map')
            self.nodemap = self.cam.GetNodeMap()

            self.cameraSerialNumC = self.nodemap_tldevice.GetNode("DeviceSerialNumber")
            self.cameraModelNameC = self.nodemap_tldevice.GetNode("DeviceModelName")
            self.cameraDisplayNameC = self.nodemap_tldevice.GetNode("DeviceDisplayName")

            self.cameraSerialNum = PySpin.CValuePtr(self.cameraSerialNumC).ToString()
            self.cameraModelName = PySpin.CValuePtr(self.cameraModelNameC).ToString()
            self.cameraDisplayName = PySpin.CValuePtr(self.cameraDisplayNameC).ToString()


            self.node_offset_x = PySpin.CIntegerPtr(self.nodemap.GetNode('OffsetX'))
            self.node_offset_y = PySpin.CIntegerPtr(self.nodemap.GetNode('OffsetY'))
            self.node_width = PySpin.CIntegerPtr(self.nodemap.GetNode('Width'))
            self.node_height = PySpin.CIntegerPtr(self.nodemap.GetNode('Height'))

            self.maxWidth = self.node_width.GetMax()
            self.minWidth = self.node_width.GetMin()
            self.currentWidth = self.node_width.GetValue()
            self.widthIncrements = self.node_width.GetInc()
            
            self.maxHeight = self.node_height.GetMax()
            self.minHeight = self.node_height.GetMin()
            self.currentheight = self.node_height.GetValue()
            self.heightIncrements = self.node_height.GetInc()

            self.currentOffsetX = self.node_offset_x.GetValue()
            self.currentOffsetY = self.node_offset_y.GetValue()
            return True
        # except:
        #     return False
    
    def stopCapture(self):
        self.captureStop = True

    def endAcquisition(self):
        # Release reference to camera
        # NOTE: Unlike the C++ examples, we cannot rely on pointer objects being automatically
        # cleaned up when going out of scope.
        # The usage of del is preferred to assigning the variable to None.

        # # Deinitialize camera
        self.cam.DeInit()
        print('Camera De initalised')
        
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
        self.cam.BeginAcquisition()

        print('Acquiring images...')

        #  Retrieve device serial number for filename
        device_serial_number = ''
        node_device_serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode('DeviceSerialNumber'))
        if PySpin.IsReadable(node_device_serial_number):
            device_serial_number = node_device_serial_number.GetValue()
            print('Device serial number retrieved as %s...' % device_serial_number)


        print(f'Recording: {continue_recording}')

        self.imageNumber = 0 #Set image number

        # Retrieve and display images
        while(continue_recording):

                #  Retrieve next received image                
                image_result = self.cam.GetNextImage(1000)

                #  Ensure image completion
                if image_result.IsIncomplete():
                    print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

                else:  

                    time_start = time.time()

                    # Getting the image data as a numpy array
                    image_data = image_result.GetNDArray()

                    print(f'Acquired image: {self.imageNumber}')

                    # Draws an image on the current figure
                    self.imageAcquired.emit(image_data, self.imageNumber)


                    # If user presses enter, close the program
                    if self.captureStop==True:
                        print('Program is closing...')
                        
                        # input('Done! Press Enter to exit...')
                        continue_recording=False

                #  Release image
                #
                #  *** NOTES ***
                #  Images retrieved directly from the camera (i.e. non-converted
                #  images) need to be released in order to keep from filling the
                #  buffer.
                image_result.Release()

                #Increment image number
                self.imageNumber += 1

            
        #  End acquisition
        #
        #  *** NOTES ***
        #  Ending acquisition appropriately helps ensure that devices clean up
        #  properly and do not need to be power-cycled to maintain integrity.
        print('Acquisition Ended')
        self.cam.EndAcquisition()

        return True

    def configure_exposure(self, exposure_time_to_set):
        """
        This function configures a custom exposure time. Automatic exposure is turned
        off in order to allow for the customization, and then the custom setting is
        applied.

        :param cam: Camera to configure exposure for.
        :type cam: CameraPtr
        :return: True if successful, False otherwise.
        :rtype: bool
        """

        print('*** CONFIGURING EXPOSURE ***\n')

        try:
            result = True

            # Turn off automatic exposure mode
            #
            # *** NOTES ***
            # Automatic exposure prevents the manual configuration of exposure
            # times and needs to be turned off for this example. Enumerations
            # representing entry nodes have been added to QuickSpin. This allows
            # for the much easier setting of enumeration nodes to new values.
            #
            # The naming convention of QuickSpin enums is the name of the
            # enumeration node followed by an underscore and the symbolic of
            # the entry node. Selecting "Off" on the "ExposureAuto" node is
            # thus named "ExposureAuto_Off".
            #
            # *** LATER ***
            # Exposure time can be set automatically or manually as needed. This
            # example turns automatic exposure off to set it manually and back
            # on to return the camera to its default state.

            if self.cam.ExposureAuto.GetAccessMode() != PySpin.RW:
                print('Unable to disable automatic exposure. Aborting...')
                return False, 'Unable to disable automatic exposure. Aborting...'

            self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
            print('Automatic exposure disabled...')

            # Set exposure time manually; exposure time recorded in microseconds
            #
            # *** NOTES ***
            # Notice that the node is checked for availability and writability
            # prior to the setting of the node. In QuickSpin, availability and
            # writability are ensured by checking the access mode.
            #
            # Further, it is ensured that the desired exposure time does not exceed
            # the maximum. Exposure time is counted in microseconds - this can be
            # found out either by retrieving the unit with the GetUnit() method or
            # by checking SpinView.

            if self.cam.ExposureTime.GetAccessMode() != PySpin.RW:
                print('Unable to set exposure time. Aborting...')
                return False, 'Unable to set exposure time. Aborting...'

            # Ensure desired exposure time does not exceed the maximum
            exposure_time_to_set = min(self.cam.ExposureTime.GetMax(), exposure_time_to_set)
            self.cam.ExposureTime.SetValue(exposure_time_to_set)

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False, f'Error: {ex}'

        return result, f'Shutter time set to {exposure_time_to_set} us...'
    
    def reset_exposure(self):
        """
        This function returns the camera to a normal state by re-enabling automatic exposure.

        :param cam: Camera to reset exposure on.
        :type cam: CameraPtr
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        try:
            result = True

            # Turn automatic exposure back on
            #
            # *** NOTES ***
            # Automatic exposure is turned on in order to return the camera to its
            # default state.

            if self.cam.ExposureAuto.GetAccessMode() != PySpin.RW:
                print('Unable to enable automatic exposure (node retrieval). Non-fatal error...')
                return False

            self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Continuous)

            print('Automatic exposure enabled...')

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False

        return result
 
    def configure_custom_image_settings(self, xFrameSize, yFrameSize, xFrameOffset, yFrameOffset):
        """
        Configures a number of settings on the camera including offsets  X and Y, width and
        height. These settings must be applied before BeginAcquisition()
        is called; otherwise, they will be read only. Also, it is important to note that
        settings are applied immediately. This means if you plan to reduce the width and
        move the x offset accordingly, you need to apply such changes in the appropriate order.

        :param nodemap: GenICam nodemap.
        :type nodemap: INodeMap
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        print('\n*** CONFIGURING CUSTOM IMAGE SETTINGS *** \n')

        try:
            result = True

            # Set new value to offset X
            if PySpin.IsReadable(self.node_offset_x) and PySpin.IsWritable(self.node_offset_x):
                self.node_offset_x.SetValue(xFrameOffset)
            else:
                print('Offset X not readable or writable...')

            # Set new value to offset Y
            if PySpin.IsReadable(self.node_offset_y) and PySpin.IsWritable(self.node_offset_y):
                self.node_offset_y.SetValue(yFrameOffset)
            else:
                print('Offset Y not readable or writable...')

            # Set new width
            if PySpin.IsReadable(self.node_width) and PySpin.IsWritable(self.node_width):
                self.node_width.SetValue(xFrameSize)
            else:
                print('Width not readable or writable...')

            # Set new height
            if  PySpin.IsReadable(self.node_height) and PySpin.IsWritable(self.node_height):
                self.node_height.SetValue(yFrameSize)
            else:
                print('Height not readable or writable...')

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False
        
        #Re obtain all frame values to update interface
        self.currentWidth = self.node_width.GetValue()
        self.currentheight = self.node_height.GetValue()
        self.currentOffsetX = self.node_offset_x.GetValue()
        self.currentOffsetY = self.node_offset_y.GetValue()

        return result



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

        self.captureStop = False

        try:
            result = True

            # Acquire images          
            result &= self.acquire_and_display_images(self.nodemap, self.nodemap_tldevice)
                

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