import numpy as np
import matplotlib.pyplot as plt
import os
import tensorflow as tf
from cv2 import imwrite
from math import floor
import time

from utils import commonFunctions as CF


from cameraSettings import CameraPipeline
from imageRecorder import ImageRecorder
from MLPipeline import machineLearningPipeline


from PyQt5.QtCore import *
from PyQt5.QtGui import QImage, QPixmap



class mainPipeline(QObject):
    updateImagePlayback = pyqtSignal(QPixmap, int)
    updateImageAcquisition = pyqtSignal(QPixmap)

    channels = 0
    model_path = ""
    dataset_path = ""

    minContrast = 0
    maxContrast = 255

    stop_pressed = False #Default False
    TFML = False #Machine learning off by default

    demo = False



    # ---- MACHINE LEARNING FUNCTIONS ---- #
    def createMLThread(self):
        # MACHINE LEARNING THREAD #
        self.machineLearningFunctions = machineLearningPipeline()
        self.machineLearningThread = QThread()
        self.machineLearningFunctions.moveToThread(self.machineLearningThread)
        self.machineLearningThread.start()
        pass

    def loadMLModel(self, modelFilepath):
        #Send model filepath to ML pipeline for loading
        self.machineLearningFunctions.loadModel(modelFilepath)
        #Get shape of input layer for display
        self.firstLayerShape = self.machineLearningFunctions.firstLayerShape





# ---- PLAYBACK FUNCTIONS ---- #
    def singleImagePlayback(self):
        outputImage = self.dataset[self.currentImageNum:self.currentImageNum+1,:,:,:]
        
        #Process image
        if self.TFML == True:
            outputImage = self.machineLearningFunctions.processStack(outputImage)
        else:
            #Need to put 4D image into 1D array
            outputImage = self.singleFrameFromStack(outputImage)
            pass
        
        #Perform contrast adjustment
        outputImage = self.contrastAdjustment(outputImage)

        #Prepare image for display
        pixOutputImage = self.prepareImageForDisplay(outputImage)
        
        #Emit image back to main page for display
        self.updateImagePlayback.emit(pixOutputImage, self.currentImageNum)

    def runPlayback(self):
        self.stop_pressed = False

        while self.stop_pressed == False:

            #Get images from dataset
            outputImage = self.dataset[self.currentImageNum:self.currentImageNum+1,:,:,:]

            #Process image
            if self.TFML == True:
                outputImage = self.machineLearningFunctions.processStack(outputImage)
            else:
                #Need to put 4D image into 1D array
                outputImage = self.singleFrameFromStack(outputImage)
                pass

            #Perform contrast adjustment
            outputImage = self.contrastAdjustment(outputImage)

            #Prepare image for display
            pix_output = self.prepareImageForDisplay(outputImage)

            #Emit image back to main page for display
            self.updateImagePlayback.emit(pix_output, self.currentImageNum)

            time.sleep(1) # wait 1 second before looping

            #check if end of dataset has been reached
            if self.currentImageNum == self.dataset.shape[0]: # 0th items in dataset is number of images (eg 10,256,256,11 dataset has 10 images)
                self.currentImageNum = 0 #If end of dataset reached loop dataset
            else:
                self.currentImageNum += 1 #Else iterate to next image

    def stopPlayback(self):
        self.stop_pressed = True



# ---- CAMERA FUNCTIONS ---- #
    def initaliseCamera(self):
        tfCameraInitalised = self.cameraFunctions.initialiseCamera()
        return tfCameraInitalised

    def runAcquisition(self):
        #Reset image number to 0
        self.currentImageNum = 0

        #Tell camera to beging acquiring
        self.cameraFunctions.run_single_camera()

        pass

    def stopAcquisition(self):
        #Tell camera to stop acquiring
        self.cameraFunctions.stopCapture()
        pass

    def processCameraImage(self, cameraImage, imageNumber):
        #When image recieved from camera:
        
        if self.TFML:
            #check if on demo
            #Demo will overlay 256x256 fibre bundle 
            if self.demo:
                cameraImage = self.applyFibereOverlay(cameraImage)

            #If ML on send image to stack
            self.sendImageToStack(cameraImage, imageNumber)
        else:
            #If ML off - Process image
            pix_output = self.singleImageFromCamera(cameraImage)
        
            # Draws an image on the current figure
            self.updateImageAcquisition.emit(pix_output)

        pass

    def processCameraStack(self, cameraStack):
        #run stack through ML model
        processedImage = self.machineLearningFunctions.processStack(cameraStack)

        #Convert to pix map
        pix_output = self.prepareImageForDisplay(processedImage)

        #Emit pixmap to GUI
        self.updateImageAcquisition.emit(pix_output)

        pass

# ---- GENERAL FUNCTIONS ---- #
    def toggleML(self, tfPerformML):
        #Update local variable to check if performing ML
        self.TFML = tfPerformML

    def toggleDemo(self, OnOff):
        #Set local variable to tur or false
        self.demo = OnOff
        #Load fibre bundle image
        self.fibreBundle = np.load('fibreMask256.png')
        #Get core locations
        self.preprocessFibre(self.fibreBundle)
        return
    
    def preprocessFibre(self, fBundle):
        self.im_denom_masked = fBundle

        labeled_array, self.num_cores = label(self.im_denom_masked)

        print('Labeled mask')

        # Find non zero values which represent pixels that 
        # are not interpolated
        nzarry, nzarrx = np.nonzero(self.im_denom_masked)
        values_known = self.im_denom_masked[nzarry,nzarrx]

        # A meshgrid of pixel coordinates
        self.m, self.n = self.im_denom_masked.shape[0], self.im_denom_masked.shape[1]
        mi, ni = self.im_denom_masked.shape[0], self.im_denom_masked.shape[1]

        [X,Y]=[nzarrx, nzarry]
        [self.Xi,self.Yi]=np.meshgrid(np.arange(0, self.n, 1), np.arange(0, self.m, 1))

        xy=np.zeros([X.shape[0],2])
        xy[:,0]=Y.flatten()
        xy[:,1]=X.flatten()

        uv=np.zeros([self.Xi.shape[0]*self.Xi.shape[1],2])
        uv[:,0]=self.Yi.flatten()
        uv[:,1]=self.Xi.flatten()

        print('Mesh grid created')

        self.core_pixel_num = np.zeros(shape=(self.num_cores+1,1),dtype=int)


        #Count cores
        unique, self.core_pixel_num = np.unique(labeled_array, return_counts=True)

        print('number of cores counted')


            
        # We need an array only of size determined by the maximum number of pixels per core    
        max_num_pixels_per_core = np.max(self.core_pixel_num[1:])

        if max_num_pixels_per_core < 10:
            max_num_pixels_per_core = 10
            print('Number of pixels per core appears to be small.')
        elif max_num_pixels_per_core >100:
            print('Number of pixels per core appears to be too big.')

        self.core_arr_x = np.zeros(shape=(self.num_cores+1,max_num_pixels_per_core),dtype=int)
        self.core_arr_y = np.zeros(shape=(self.num_cores+1,max_num_pixels_per_core),dtype=int)
        self.core_arr_vals = np.zeros(shape=(self.num_cores+1,max_num_pixels_per_core),dtype=float)
        self.core_arr_vals_bool = np.full((self.num_cores+1,max_num_pixels_per_core),False,dtype=bool)
        self.core_arr_mean = np.zeros(shape=(self.num_cores+1,1),dtype=float)

        #Core locations
        self.core_arr_x, self.core_arr_y, self.core_arr_vals_bool = CF.core_locations(labeled_array, self.num_cores, self.core_pixel_num, self.core_arr_x, self.core_arr_y, self.core_arr_vals_bool)
        print('core locations obtained')

        self.idxpts=np.arange(1,self.num_cores+1)

    def averageCores(self, im):
        # ---- Average cores ---- #
        # Copy core values from image to core array. The array is initialised to 0 beforehand.
        self.core_arr_vals[self.idxpts,:] = im[self.core_arr_y[self.idxpts,:],self.core_arr_x[self.idxpts,:]]

        # Calculate mean value per core. The boolean array within "where" was preset to be True
        # for array locations where core values are expected and False for array locations where no
        # no value is expected. With optics used, maximum 70-80 pixels per core is expected.
        core_arr_mean = np.mean(self.core_arr_vals, axis=1, where=self.core_arr_vals_bool)

        # Remap back to image the means of whole core back into image. For some reason, I could not vectorise 
        # code below, hence the for loop. Trying to figure out the limitations of vectorisation.
        im[self.core_arr_y[self.idxpts,:],self.core_arr_x[self.idxpts,:]] = core_arr_mean[self.idxpts, None]

        

    def contrastChanged(self, minCont, maxCont):
        #Update thread contrast values
        self.minContrast = minCont
        self.maxContrast = maxCont
        #Run single image incase playback is paused
        if self.stop_pressed:
            self.singleImageML()
     
    def loadDataset(self, dataset_fp):
        #Copy file path to thread
        self.dataset_path = dataset_fp   

        #Load the dataset
        self.dataset = np.load(self.dataset_path)

        #Set current image number to 0
        self.currentImageNum = 0

        #Return the shape of the dataset for UI features
        return self.dataset.shape

    def currentImageUpdated(self, imageNo):
        #Set thread current image value to new value
        self.currentImageNum = imageNo

        #Run ML and output new image
        self.singleImagePlayback()

    def contrastAdjustment(self, outputImage):
        outputImage = CF.AdjustContrastImage(outputImage, self.minContrast, self.maxContrast)
        return outputImage

    def prepareImageForDisplay(self, outputImage):
        height,width = outputImage.shape
        bytesPerLine = width            
        arrCombined = np.require(outputImage, np.uint8, 'C')
        qImg = QImage(arrCombined.data, width, height, bytesPerLine, QImage.Format_Grayscale8)
        pixOutput = QPixmap.fromImage(qImg)

        return pixOutput

    def singleFrameFromStack(self, imageStack):
        #Get the first image in the stack with only the first channel
        singleFrame = imageStack[0,:,:,0]
        #Multiply by 255 to get values between 1 and 256 instead of 0 and 1
        singleFrame *= 255
        return singleFrame



    def singleImageFromCamera(self,cameraImage):
        height,width = cameraImage.shape
        imgOut = np.zeros((height,width,3))
        #Format is RGB
        imgOut[:,:,0] = cameraImage
        imgOut[:,:,1] = cameraImage
        imgOut[:,:,2] = cameraImage

        bytesPerLine = 3*width            
        arrCombined = np.require(imgOut, np.uint8, 'C')
        qImg = QImage(arrCombined.data, width, height, bytesPerLine, QImage.Format_RGB888)
        pix_output = QPixmap.fromImage(qImg)
        return pix_output
    
    def createCameraThread(self):
        # CAMERA THREAD #
        self.cameraFunctions = CameraPipeline()
        self.cameraThread = QThread()
        self.cameraFunctions.moveToThread(self.cameraThread)
        self.cameraThread.start()

        #Slot to recieve image from camera
        self.cameraFunctions.imageAcquired.connect(self.processCameraStack)

        # RECORDER THREAD #
        self.recorderFunctions = ImageRecorder()
        self.recorderThread = QThread()
        self.recorderFunctions.moveToThread(self.recorderThread)
        self.recorderThread.start()

        #Slot to recieve full stack from recorder
        self.recorderFunctions.stackFull.connect(self.machineLearningFunctions.processStack)

    def stopCameraThread(self):
        #Exit camera thread
        self.cameraThread.exit() 

        #Exit recorder thread
        self.recorderThread.exit()
        pass

    def setCameraSettings(self, MLInputShape, exposureTime):
        #Copy ML shape for buffer shape
        self.mlShape = MLInputShape
        #Copy exposure time for initial setup
        self.exposureTime = exposureTime

    def setCameraFrameSize(self, xFrameSize, yFrameSize, xFrameOffset, yFrameOffset):
        #Perform checks
        #Camera frame goes outside X range
        if xFrameSize + xFrameOffset > self.cameraFunctions.maxWidth:
            return False
        #Camera frame goes outside Y range
        if yFrameSize + yFrameOffset > self.cameraFunctions.maxHeight:
            return False
        
        try:
            self.cameraFunctions.configure_custom_image_settings(xFrameSize, yFrameSize, xFrameOffset, yFrameOffset)
            return True
        except:
            return False

    def createSaveStack(self):
        #Pass mlshape to image recorder class
        self.recorderFunctions.createSaveBuffer(self.mlShape)

    def sendImageToStack(self, image, imageNum):
        self.recorderFunctions.addImageToDisplayStack(image, imageNum)

    def setSaveLocation(self, newSavePath):
        #Update local path to new path
        self.savePath = newSavePath

    def saveImageStack(self):
        #Tell image recorder thread to save stack
        self.recorderFunctions.saveImages(self.savePath)
        pass


    def applyFibereOverlay(self, image):
        #apply fibre bundle
        imageOverlayed = image * self.fibreBundle

        #Average cores
        imageAveraged = CF.

        return