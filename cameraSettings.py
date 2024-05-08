

# import PySpin
# import matplotlib.pyplot as plt
# import sys
# import keyboard

# import numpy as np

# import time

# from PyQt5.QtCore import *
# from PyQt5.QtWidgets import *
# from PyQt5.QtGui import *

# class TriggerType:
#     SOFTWARE = 1
#     HARDWARE = 2




# class CameraThread(QObject):
#     imageAcquired = pyqtSignal(QPixmap)
#     updateFPS = pyqtSignal(int)


 
#     CHOSEN_TRIGGER = TriggerType.SOFTWARE

#     global continue_recording
#     continue_recording = True

#     def initialise(self):
#         """
#         Example entry point; notice the volume of data that the logging event handler
#         prints out on debug despite the fact that very little really happens in this
#         example. Because of this, it may be better to have the logger set to lower
#         level in order to provide a more concise, focused log.

#         :return: True if successful, False otherwise.
#         :rtype: bool
#         """
#         result = True

#         # Retrieve singleton reference to system object
#         self.system = PySpin.System.GetInstance()

#         # Get current library version
#         version = self.system.GetLibraryVersion()
#         print('Library version: %d.%d.%d.%d' % (version.major, version.minor, version.type, version.build))

#         # Retrieve list of cameras from the system
#         self.cam_list = self.system.GetCameras()

#         num_cameras = self.cam_list.GetSize()

#         print('Number of cameras detected: %d' % num_cameras)

#         # Finish if there are no cameras
#         if num_cameras == 0:

#             # Clear camera list before releasing system
#             self.cam_list.Clear()

#             # Release system instance
#             self.system.ReleaseInstance()

#             print('Not enough cameras!')
#             return False
        
#         return result
    
#     def exit(self):
#         self.captureStop = True

#     def endAcquisition(self):
#         # Release reference to camera
#         # NOTE: Unlike the C++ examples, we cannot rely on pointer objects being automatically
#         # cleaned up when going out of scope.
#         # The usage of del is preferred to assigning the variable to None.
#         del self.cam

#         # Clear camera list before releasing system
#         self.cam_list.Clear()

#         # Release system instance
#         self.system.ReleaseInstance()

#         print('Acquisition ended.')

#     def acquire_by_trigger(self, nodemap, nodemap_tldevice):
#         global continue_recording
#         continue_recording = True
        
#         try:
#             result = True

#             # Set acquisition mode to continuous
#             # In order to access the node entries, they have to be casted to a pointer type (CEnumerationPtr here)
#             node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
#             if not PySpin.IsReadable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
#                 print('Unable to set acquisition mode to continuous (enum retrieval). Aborting...')
#                 return False

#             # Retrieve entry node from enumeration node
#             node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
#             if not PySpin.IsReadable(node_acquisition_mode_continuous):
#                 print('Unable to set acquisition mode to continuous (entry retrieval). Aborting...')
#                 return False

#             # Retrieve integer value from entry node
#             acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

#             # Set integer value from entry node as new value of enumeration node
#             node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

#             print('Acquisition mode set to continuous...')

#             #  Begin acquiring images
#             self.cam.BeginAcquisition()

#             print('Acquiring images...')

#             #  Retrieve device serial number for filename
#             #
#             #  *** NOTES ***
#             #  The device serial number is retrieved in order to keep cameras from
#             #  overwriting one another. Grabbing image IDs could also accomplish
#             #  this.
#             device_serial_number = ''
#             node_device_serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode('DeviceSerialNumber'))
#             if PySpin.IsReadable(node_device_serial_number):
#                 device_serial_number = node_device_serial_number.GetValue()
#                 print('Device serial number retrieved as %s...' % device_serial_number)

#             # Retrieve, convert, and save images

#             # Create ImageProcessor instance for post processing images
#             processor = PySpin.ImageProcessor()

#             # Set default image processor color processing method
#             #
#             # *** NOTES ***
#             # By default, if no specific color processing algorithm is set, the image
#             # processor will default to NEAREST_NEIGHBOR method.
#             processor.SetColorProcessing(PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_HQ_LINEAR)

#             while(continue_recording):
#                 try:

#                     #  Retrieve the next image from the trigger
#                     # result &= grab_next_image_by_trigger(nodemap, self.cam)

#                     #  Retrieve next received image
#                     print('Retrieving image')
#                     image_result = self.cam.GetNextImage(PySpin.EVENT_TIMEOUT_INFINITE) #PySpin.EVENT_TIMEOUT_INFINITE

#                     #  Ensure image completion
#                     if image_result.IsIncomplete():
#                         print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

#                     else:
#                         time_start = time.time()

#                         # Getting the image data as a numpy array
#                         image_data = image_result.GetNDArray()

#                         height,width = image_data.shape
#                         imgOut = np.zeros((height,width,3))
#                         #Format is RGB
#                         imgOut[:,:,1] = image_data
#                         bytesPerLine = 3*width            
#                         arrCombined = np.require(imgOut, np.uint8, 'C')
#                         qImg = QImage(arrCombined.data, width, height, bytesPerLine, QImage.Format_RGB888)
#                         pixmap = QPixmap.fromImage(qImg)


#                         # Draws an image on the current figure
#                         self.imageAcquired.emit(pixmap.scaled(720,512, aspectRatioMode=Qt.KeepAspectRatio))

#                         time_stop = time.time()

#                         self.updateFPS.emit(int(np.round(1/(time_stop - time_start),0)))


#                         # If user presses enter, close the program
#                         if self.captureStop==True:
#                             print('Program is closing...')
                            
#                             # Close figure
#                             plt.close('all')   

#                             # input('Done! Press Enter to exit...')
#                             continue_recording=False

#                         image_result.Release()

#                 except PySpin.SpinnakerException as ex:
#                     print('Error: %s' % ex)
#                     return False

#             # End acquisition
#             #
#             #  *** NOTES ***
#             #  Ending acquisition appropriately helps ensure that devices clean up
#             #  properly and do not need to be power-cycled to maintain integrity.
#             self.cam.EndAcquisition()

#         except PySpin.SpinnakerException as ex:
#             print('Error: %s' % ex)
#             return False

#         return result
           
#     def acquire_and_display_images(self, nodemap, nodemap_tldevice):
#         """
#         This function continuously acquires images from a device and display them in a GUI.

#         :param cam: Camera to acquire images from.
#         :param nodemap: Device nodemap.
#         :param nodemap_tldevice: Transport layer device nodemap.
#         :type cam: CameraPtr
#         :type nodemap: INodeMap
#         :type nodemap_tldevice: INodeMap
#         :return: True if successful, False otherwise.
#         :rtype: bool
#         """
#         global continue_recording
#         continue_recording = True

#         sNodemap = self.cam.GetTLStreamNodeMap()

#         # Change bufferhandling mode to NewestOnly
#         node_bufferhandling_mode = PySpin.CEnumerationPtr(sNodemap.GetNode('StreamBufferHandlingMode'))
#         if not PySpin.IsReadable(node_bufferhandling_mode) or not PySpin.IsWritable(node_bufferhandling_mode):
#             print('Unable to set stream buffer handling mode.. Aborting...')
#             return False

#         # Retrieve entry node from enumeration node
#         node_newestonly = node_bufferhandling_mode.GetEntryByName('NewestOnly')
#         if not PySpin.IsReadable(node_newestonly):
#             print('Unable to set stream buffer handling mode.. Aborting...')
#             return False

#         # Retrieve integer value from entry node
#         node_newestonly_mode = node_newestonly.GetValue()

#         # Set integer value from entry node as new value of enumeration node
#         node_bufferhandling_mode.SetIntValue(node_newestonly_mode)

#         print('*** IMAGE ACQUISITION ***\n')
#         try:
#             node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
#             if not PySpin.IsReadable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
#                 print('Unable to set acquisition mode to continuous (enum retrieval). Aborting...')
#                 return False

#             # Retrieve entry node from enumeration node
#             node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
#             if not PySpin.IsReadable(node_acquisition_mode_continuous):
#                 print('Unable to set acquisition mode to continuous (entry retrieval). Aborting...')
#                 return False

#             # Retrieve integer value from entry node
#             acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

#             # Set integer value from entry node as new value of enumeration node
#             node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

#             print('Acquisition mode set to continuous...')

#             #  Begin acquiring images
#             #
#             #  *** NOTES ***
#             #  What happens when the camera begins acquiring images depends on the
#             #  acquisition mode. Single frame captures only a single image, multi
#             #  frame catures a set number of images, and continuous captures a
#             #  continuous stream of images.
#             #
#             #  *** LATER ***
#             #  Image acquisition must be ended when no more images are needed.
#             self.cam.BeginAcquisition()

#             print('Acquiring images...')

#             #  Retrieve device serial number for filename
#             #
#             #  *** NOTES ***
#             #  The device serial number is retrieved in order to keep cameras from
#             #  overwriting one another. Grabbing image IDs could also accomplish
#             #  this.
#             device_serial_number = ''
#             node_device_serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode('DeviceSerialNumber'))
#             if PySpin.IsReadable(node_device_serial_number):
#                 device_serial_number = node_device_serial_number.GetValue()
#                 print('Device serial number retrieved as %s...' % device_serial_number)

#             # Close program
#             print('Press enter to close the program..')

#             # # Figure(1) is default so you can omit this line. Figure(0) will create a new window every time program hits this line
#             # # Close the GUI when close event happens
#             # fig.canvas.mpl_connect('close_event', self.handle_close)

#             print(f'Recording: {continue_recording}')

#             # Retrieve and display images
#             while(continue_recording):
#                 try:

#                     #  Retrieve next received image
#                     #
#                     #  *** NOTES ***
#                     #  Capturing an image houses images on the camera buffer. Trying
#                     #  to capture an image that does not exist will hang the camera.
#                     #
#                     #  *** LATER ***
#                     #  Once an image from the buffer is saved and/or no longer
#                     #  needed, the image must be released in order to keep the
#                     #  buffer from filling up.
                    
#                     image_result = self.cam.GetNextImage(1000)

#                     #  Ensure image completion
#                     if image_result.IsIncomplete():
#                         print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

#                     else:  

#                         time_start = time.time()

#                         # Getting the image data as a numpy array
#                         image_data = image_result.GetNDArray()

#                         height,width = image_data.shape
#                         imgOut = np.zeros((height,width,3))
#                         #Format is RGB
#                         imgOut[:,:,1] = image_data
#                         bytesPerLine = 3*width            
#                         arrCombined = np.require(imgOut, np.uint8, 'C')
#                         qImg = QImage(arrCombined.data, width, height, bytesPerLine, QImage.Format_RGB888)
#                         pixmap = QPixmap.fromImage(qImg)


#                         # Draws an image on the current figure
#                         self.imageAcquired.emit(pixmap.scaled(720,512, aspectRatioMode=Qt.KeepAspectRatio))

#                         time_stop = time.time()

#                         self.updateFPS.emit(int(np.round(1/(time_stop - time_start),0)))


#                         # If user presses enter, close the program
#                         if self.captureStop==True:
#                             print('Program is closing...')
                            
#                             # Close figure
#                             plt.close('all')   

#                             # input('Done! Press Enter to exit...')
#                             continue_recording=False

#                     #  Release image
#                     #
#                     #  *** NOTES ***
#                     #  Images retrieved directly from the camera (i.e. non-converted
#                     #  images) need to be released in order to keep from filling the
#                     #  buffer.
#                     image_result.Release()

#                 except PySpin.SpinnakerException as ex:
#                     print('Error: %s' % ex)
#                     return False
                
#             #  End acquisition
#             #
#             #  *** NOTES ***
#             #  Ending acquisition appropriately helps ensure that devices clean up
#             #  properly and do not need to be power-cycled to maintain integrity.
#             self.cam.EndAcquisition()
            
#         except PySpin.SpinnakerException as ex:
#             print('Error: %s' % ex)
#             return False

#         return True
    
#     def setTrigger(self, triggerMode):
#         print(f'Trigger mode: {triggerMode}')
#         if triggerMode == 1:
#             self.CHOSEN_TRIGGER = TriggerType.SOFTWARE
#         elif triggerMode == 2:
#             self.CHOSEN_TRIGGER = TriggerType.HARDWARE
#         else:
#             print("Error changing trigger mode")

#         print(f'chosen trigger: {self.CHOSEN_TRIGGER}')

#     def configure_trigger(self):
#         """
#         This function configures the camera to use a trigger. First, trigger mode is
#         set to off in order to select the trigger source. Once the trigger source
#         has been selected, trigger mode is then enabled, which has the camera
#         capture only a single image upon the execution of the chosen trigger.

#         :param cam: Camera to configure trigger for.
#         :type cam: CameraPtr
#         :return: True if successful, False otherwise.
#         :rtype: bool
#         """
#         result = True

#         print('*** CONFIGURING TRIGGER ***\n')

#         print('Note that if the application / user software triggers faster than frame time, the trigger may be dropped / skipped by the camera.\n')
#         print('If several frames are needed per trigger, a more reliable alternative for such case, is to use the multi-frame mode.\n\n')

#         if self.CHOSEN_TRIGGER == TriggerType.SOFTWARE:
#             print('Software trigger chosen ...')
#         elif self.CHOSEN_TRIGGER == TriggerType.HARDWARE:
#             print('Hardware trigger chose ...')

#         try:
#             # Ensure trigger mode off
#             # The trigger must be disabled in order to configure whether the source
#             # is software or hardware.
#             nodemap = self.cam.GetNodeMap()
#             node_trigger_mode = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerMode'))
#             if not PySpin.IsReadable(node_trigger_mode) or not PySpin.IsWritable(node_trigger_mode):
#                 print('Unable to disable trigger mode (node retrieval). Aborting...')
#                 return False

#             node_trigger_mode_off = node_trigger_mode.GetEntryByName('Off')
#             if not PySpin.IsReadable(node_trigger_mode_off):
#                 print('Unable to disable trigger mode (enum entry retrieval). Aborting...')
#                 return False

#             node_trigger_mode.SetIntValue(node_trigger_mode_off.GetValue())

#             print('Trigger mode disabled...')

#             # Set TriggerSelector to FrameStart
#             # For this example, the trigger selector should be set to frame start.
#             # This is the default for most cameras.
#             node_trigger_selector= PySpin.CEnumerationPtr(nodemap.GetNode('TriggerSelector'))
#             if not PySpin.IsReadable(node_trigger_selector) or not PySpin.IsWritable(node_trigger_selector):
#                 print('Unable to get trigger selector (node retrieval). Aborting...')
#                 return False

#             node_trigger_selector_framestart = node_trigger_selector.GetEntryByName('FrameStart')
#             if not PySpin.IsReadable(node_trigger_selector_framestart):
#                 print('Unable to set trigger selector (enum entry retrieval). Aborting...')
#                 return False
#             node_trigger_selector.SetIntValue(node_trigger_selector_framestart.GetValue())

#             print('Trigger selector set to frame start...')

#             # Select trigger source
#             # The trigger source must be set to hardware or software while trigger
#             # mode is off.
#             node_trigger_source = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerSource'))
#             if not PySpin.IsReadable(node_trigger_source) or not PySpin.IsWritable(node_trigger_source):
#                 print('Unable to get trigger source (node retrieval). Aborting...')
#                 return False

#             if self.CHOSEN_TRIGGER == TriggerType.SOFTWARE:
#                 node_trigger_source_software = node_trigger_source.GetEntryByName('Software')

#                 print("TRIGGER SET TO SOFTWARE")

#                 if not PySpin.IsReadable(node_trigger_source_software):
#                     print('Unable to get trigger source (enum entry retrieval). Aborting...')
#                     return False
#                 node_trigger_source.SetIntValue(node_trigger_source_software.GetValue())
#                 print('Trigger source set to software...')

#             elif self.CHOSEN_TRIGGER == TriggerType.HARDWARE:
#                 node_trigger_source_hardware = node_trigger_source.GetEntryByName('Line0')
#                 if not PySpin.IsReadable(node_trigger_source_hardware):
#                     print('Unable to get trigger source (enum entry retrieval). Aborting...')
#                     return False
#                 node_trigger_source.SetIntValue(node_trigger_source_hardware.GetValue())
#                 print('Trigger source set to hardware...')

#             # Turn trigger mode on
#             # Once the appropriate trigger source has been set, turn trigger mode
#             # on in order to retrieve images using the trigger.
#             node_trigger_mode_on = node_trigger_mode.GetEntryByName('On')
#             if not PySpin.IsReadable(node_trigger_mode_on):
#                 print('Unable to enable trigger mode (enum entry retrieval). Aborting...')
#                 return False

#             node_trigger_mode.SetIntValue(node_trigger_mode_on.GetValue())
#             print('Trigger mode turned back on...')

#         except PySpin.SpinnakerException as ex:
#             print('Error: %s' % ex)
#             return False

#         return result

#     def configure_exposure(cam, exposure_time_to_set):
#         """
#         This function configures a custom exposure time. Automatic exposure is turned
#         off in order to allow for the customization, and then the custom setting is
#         applied.

#         :param cam: Camera to configure exposure for.
#         :type cam: CameraPtr
#         :return: True if successful, False otherwise.
#         :rtype: bool
#         """

#         print('*** CONFIGURING EXPOSURE ***\n')

#         try:
#             result = True

#             # Turn off automatic exposure mode
#             #
#             # *** NOTES ***
#             # Automatic exposure prevents the manual configuration of exposure
#             # times and needs to be turned off for this example. Enumerations
#             # representing entry nodes have been added to QuickSpin. This allows
#             # for the much easier setting of enumeration nodes to new values.
#             #
#             # The naming convention of QuickSpin enums is the name of the
#             # enumeration node followed by an underscore and the symbolic of
#             # the entry node. Selecting "Off" on the "ExposureAuto" node is
#             # thus named "ExposureAuto_Off".
#             #
#             # *** LATER ***
#             # Exposure time can be set automatically or manually as needed. This
#             # example turns automatic exposure off to set it manually and back
#             # on to return the camera to its default state.

#             if cam.ExposureAuto.GetAccessMode() != PySpin.RW:
#                 print('Unable to disable automatic exposure. Aborting...')
#                 return False

#             cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
#             print('Automatic exposure disabled...')

#             # Set exposure time manually; exposure time recorded in microseconds
#             #
#             # *** NOTES ***
#             # Notice that the node is checked for availability and writability
#             # prior to the setting of the node. In QuickSpin, availability and
#             # writability are ensured by checking the access mode.
#             #
#             # Further, it is ensured that the desired exposure time does not exceed
#             # the maximum. Exposure time is counted in microseconds - this can be
#             # found out either by retrieving the unit with the GetUnit() method or
#             # by checking SpinView.

#             if cam.ExposureTime.GetAccessMode() != PySpin.RW:
#                 print('Unable to set exposure time. Aborting...')
#                 return False

#             # Ensure desired exposure time does not exceed the maximum
#             exposure_time_to_set = 500000.0
#             exposure_time_to_set = min(cam.ExposureTime.GetMax(), exposure_time_to_set)
#             cam.ExposureTime.SetValue(exposure_time_to_set)
#             print('Shutter time set to %s us...\n' % exposure_time_to_set)

#         except PySpin.SpinnakerException as ex:
#             print('Error: %s' % ex)
#             result = False

#         return result
    
#     def reset_exposure(cam):
#         """
#         This function returns the camera to a normal state by re-enabling automatic exposure.

#         :param cam: Camera to reset exposure on.
#         :type cam: CameraPtr
#         :return: True if successful, False otherwise.
#         :rtype: bool
#         """
#         try:
#             result = True

#             # Turn automatic exposure back on
#             #
#             # *** NOTES ***
#             # Automatic exposure is turned on in order to return the camera to its
#             # default state.

#             if cam.ExposureAuto.GetAccessMode() != PySpin.RW:
#                 print('Unable to enable automatic exposure (node retrieval). Non-fatal error...')
#                 return False

#             cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Continuous)

#             print('Automatic exposure enabled...')

#         except PySpin.SpinnakerException as ex:
#             print('Error: %s' % ex)
#             result = False

#         return result



#     @pyqtSlot()
#     def run_single_camera(self):
#         """
#         This function acts as the body of the example; please see NodeMapInfo example
#         for more in-depth comments on setting up cameras.

#         :param cam: Camera to run on.
#         :type cam: CameraPtr
#         :return: True if successful, False otherwise.
#         :rtype: bool
#         """

#         self.cam = self.cam_list[0]

#         self.captureStop = False

#         try:
#             result = True

#             nodemap_tldevice = self.cam.GetTLDeviceNodeMap()

#             # Initialize camera
#             self.cam.Init()

#             # Retrieve GenICam nodemap
#             nodemap = self.cam.GetNodeMap()

#             # Acquire images
#             # 
#             # Configure trigger
#             # if self.configure_trigger() is False:
#             #     return False
            
#             if self.CHOSEN_TRIGGER == 2:
#                 print('Acquiring by trigger')
#                 result &= self.acquire_by_trigger(nodemap, nodemap_tldevice)
#             elif self.CHOSEN_TRIGGER == 1:
#                 print('Acquiring by software')
#                 result &= self.acquire_and_display_images(nodemap, nodemap_tldevice)
                

#             # # Deinitialize camera
#             self.cam.DeInit()

#         except PySpin.SpinnakerException as ex:
#             print('Error: %s' % ex)
#             result = False

#         # try:
#         #     self.endAcquisition()

#         # except PySpin.SpinnakerException as ex:
#         #     print('Error: %s' % ex)
#         #     result = False

#         print('Program Exited')
#         return result