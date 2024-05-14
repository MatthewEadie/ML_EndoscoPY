import numpy as np
import cv2

import os

from scipy.ndimage import label
from matplotlib import pyplot as plt

from utils import method2 as M2
from utils import method1 as M1
from utils import commonFunctions as CF

from DisplaySettings import displaySettings

from PyQt5.QtCore import *
from PyQt5.QtGui import QImage, QPixmap




class playbackMethod(QObject):
    updateImage = pyqtSignal(QPixmap, QPixmap, QPixmap, QPixmap)

    global continue_playback
    continue_playback = True

    #static variables
    _selectedDataset = ""
    _imgBackgroundBlue = 0
    im_denom = 0
    binary_image = 0
    core_arr_vals = 0
    core_arr_vals_bool = 0
    idxpts = 0
    core_arr_x = 0
    core_arr_y = 0
    num_cores = 0
    vtx = 0
    wts = 0
    m = 0
    n = 0
    processedImage = 0

    gaussianKernelSigma = 5.0

    reconstructionMethod = "InterpolationOld"

    _blueChannelDisplaySettings = displaySettings()
    _RedChannelDisplaySettings = displaySettings()
    _NIRChannelDisplaySettings = displaySettings()

    

    # def __init__(self):
    #     pass

    def setAllValues(self, LED_Channel, channelSettings):
        if(LED_Channel == 1):
            self._blueChannelDisplaySettings.minValue = channelSettings.minValue
            self._blueChannelDisplaySettings.maxValue = channelSettings.maxValue
            self._blueChannelDisplaySettings.autocontrast = channelSettings.autocontrast
            self._blueChannelDisplaySettings.LEDisEnabled = channelSettings.LEDisEnabled # only relevant for Versicolour
            self._blueChannelDisplaySettings.displayMode = channelSettings.displayMode
            self._blueChannelDisplaySettings.subtractBackground = channelSettings.subtractBackground
            self._blueChannelDisplaySettings.normaliseByLightfield = channelSettings.normaliseByLightfield
        elif(LED_Channel == 2):
            self._RedChannelDisplaySettings.minValue = channelSettings.minValue
            self._RedChannelDisplaySettings.maxValue = channelSettings.maxValue
            self._RedChannelDisplaySettings.autocontrast = channelSettings.autocontrast
            self._RedChannelDisplaySettings.LEDisEnabled = channelSettings.LEDisEnabled # only relevant for Versicolour
            self._RedChannelDisplaySettings.displayMode = channelSettings.displayMode
            self._RedChannelDisplaySettings.subtractBackground = channelSettings.subtractBackground
            self._RedChannelDisplaySettings.normaliseByLightfield = channelSettings.normaliseByLightfield

        elif(LED_Channel == 3):
            self._NIRChannelDisplaySettings.minValue = channelSettings.minValue
            self._NIRChannelDisplaySettings.maxValue = channelSettings.maxValue
            self._NIRChannelDisplaySettings.autocontrast = channelSettings.autocontrast
            self._NIRChannelDisplaySettings.LEDisEnabled = channelSettings.LEDisEnabled # only relevant for Versicolour
            self._NIRChannelDisplaySettings.displayMode = channelSettings.displayMode
            self._NIRChannelDisplaySettings.subtractBackground = channelSettings.subtractBackground
            self._NIRChannelDisplaySettings.normaliseByLightfield = channelSettings.normaliseByLightfield

        else:
             print('ERROR CHANGING CHANNEL SETTINGS')
             return

    def endPlayback(self):
        self.playbackStop = True

    def newSession(self, folderPath, exposure=25):
        #Get calibration images from selected folder

        self._folderPath = folderPath

        calibFiles = os.listdir(f'{self._folderPath}/Calibration Data/Exposure_{exposure}ms/')

        self._imgBackgroundBlue = cv2.imread(f'{self._folderPath}/Calibration Data/Exposure_{exposure}ms/{calibFiles[0]}',0).astype(np.float32)
        self._imgLightfieldBlue = cv2.imread(f'{self._folderPath}/Calibration Data/Exposure_{exposure}ms/{calibFiles[1]}',0).astype(np.float32)

        # self._imgBackgroundNIR = cv2.imread(f'{folderPath}/Calibration Data/Exposure_{exposure}ms/{calibFiles[1]}',0)
        # self._imgLightfieldNIR = cv2.imread(f'{folderPath}/Calibration Data/Exposure_{exposure}ms/{calibFiles[4]}',0)

        # self._imgBackgroundRed = cv2.imread(f'{folderPath}/Calibration Data/Exposure_{exposure}ms/{calibFiles[2]}',0)
        # self._imgLightfieldRed = cv2.imread(f'{folderPath}/Calibration Data/Exposure_{exposure}ms/{calibFiles[5]}',0)

        #Check if there's a binary mask in generated data
        generatedBinaryMaskTF = os.listdir(f'{self._folderPath}/Generated Data/')
        if(generatedBinaryMaskTF):
             self.useingGeneratedMask = True
             self.im_denom_masked = cv2.imread(f'{self._folderPath}/Generated Data/{generatedBinaryMaskTF[0]}',0).astype(np.uint8)
        else:
             self.useingGeneratedMask = False



        self._imageHeightProcessing, self._imageWidthProcessing = self._imgBackgroundBlue.shape


        self.preprocessing()
        return True
    
    def updateSelectedDataset(self, selectedDataset):
         self._selectedDataset = f'{self._folderPath}/Imaging Data/{selectedDataset}'
         print(f'Selected dataset: {self._selectedDataset}')

    def average_cores(self, core_arr, core_arr_bool, idx, im, core_x, core_y, num_cores):
        # Copy core values from image to core array. The array is initialised to 0 beforehand.
        self.core_arr_vals[idx,:] = im[self.core_arr_y[idx,:],core_x[idx,:]]

        # Calculate mean value per core. The boolean array within "where" was preset to be True
        # for array locations where core values are expected and False for array locations where no
        # no value is expected. With optics used, maximum 70-80 pixels per core is expected.
        core_arr_mean = np.mean(core_arr,axis=1,where=core_arr_bool)

        # Remap back to image the means of whole core back into image. For some reason, I could not vectorise 
        # code below, hence the for loop. Trying to figure out the limitations of vectorisation.
        im[core_y[idx,:],core_x[idx,:]] = core_arr_mean[idx, None]

    def createBinaryCoreMask(self):
        self.im_denom = cv2.subtract(self._imgLightfieldBlue, self._imgBackgroundBlue)
        self.im_denom = self.im_denom.astype(np.uint8)
        minimum_thres = 38
        ret, self.binary_image = cv2.threshold(self.im_denom, minimum_thres, 255, cv2.THRESH_BINARY)
        self.im_denom_masked = cv2.bitwise_and(self.im_denom,self.im_denom,mask = self.binary_image)

        print(f'Binary mask created.')

    def preprocessing(self):

        if(self.useingGeneratedMask):
             print('using pre generated mask')
             pass
        else:
             self.createBinaryCoreMask()

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

        self.vtx, self.wts = M2.interp_weights(xy, uv)

        print('weights made')

        self.im_denom = cv2.subtract(self._imgLightfieldBlue, self._imgBackgroundBlue)

        self.core_pixel_num = np.zeros(shape=(self.num_cores+1,1),dtype=int)



        #CHANGE TO USE CF CORE COUNT
        # for kk in range(1,num_cores+1):
        #     core_pixel_num[kk] = np.shape((np.where(labeled_array==kk)))[1]

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

        #Compute Kernal size
        self.kernalSizeGauss = M1.computeGaussianKernelSizeFromSigma(self.gaussianKernelSigma)

        self.idxpts=np.arange(1,self.num_cores+1)

        print('Finished pre processing')

    @pyqtSlot()
    def GetCombinedImage(self):
        continue_playback = True
        self.playbackStop = False

        print('begining playback')

        imageIndex = 0

        datasetImages = os.listdir(f'{self._selectedDataset}/')

        while(continue_playback):
            
            imgOut_Blue = np.zeros((self._imageHeightProcessing, self._imageWidthProcessing,3))
            imgOut_Red = np.zeros((self._imageHeightProcessing, self._imageWidthProcessing,3))
            imgOut_NIR = np.zeros((self._imageHeightProcessing, self._imageWidthProcessing,3))
            imgOut_Merged = np.zeros((self._imageHeightProcessing, self._imageWidthProcessing,3))


            # check number of LEDs active
            activeLEDS = [self._blueChannelDisplaySettings.LEDisEnabled, self._RedChannelDisplaySettings.LEDisEnabled, self._NIRChannelDisplaySettings.LEDisEnabled]

            # channelID = 0
            # channelONOFF = True
            # im_output = self.processTissue(channelID, channelONOFF, datasetImages, imageIndex)

            for channelID, channelONOFF in enumerate(activeLEDS):
                print(f'channelID: {channelID}')
                print(f'channelONOFF: {channelONOFF}')
                im_output = self.processTissue(channelID, channelONOFF, datasetImages, imageIndex)

                if channelID == 0:
                    imgOut_Blue[:,:,1] = im_output
                elif channelID == 1:
                    imgOut_Red[:,:,0] = im_output
                elif channelID == 2:
                    imgOut_NIR[:,:,2] = im_output

            #RGB
            imgOut_Merged[:,:,0] = imgOut_Red[:,:,0]
            imgOut_Merged[:,:,1] = imgOut_Blue[:,:,1]
            imgOut_Merged[:,:,2] = imgOut_NIR[:,:,2]

            print('output new image')

            #Change array to pixmaps
            imgOut_Merged, imgOut_Red, imgOut_Blue, imgOut_NIR = self.createPixmaps(imgOut_Merged, imgOut_Red, imgOut_Blue, imgOut_NIR)

            self.updateImage.emit(imgOut_Merged, imgOut_Red, imgOut_Blue, imgOut_NIR)

            if self.playbackStop==True:
                continue_playback=False


            #move over each image in dataset
            if imageIndex == len(datasetImages)-1:
                imageIndex = 0
            else:
                imageIndex += 1

    def createPixmaps(self, imgOut_Merged, imgOut_Red, imgOut_Blue, imgOut_NIR):
        
        height,width,channels = imgOut_Merged.shape
        bytesPerLine = 3*width            
        arrCombined = np.require(imgOut_Merged, np.uint8, 'C')
        qImg = QImage(arrCombined.data, width, height, bytesPerLine, QImage.Format_RGB888)
        pix_Merged = QPixmap.fromImage(qImg)


        # Format is RGB
        bytesPerLine = 3*width            
        arrCombined = np.require(imgOut_Red, np.uint8, 'C')
        qImg = QImage(arrCombined.data, width, height, bytesPerLine, QImage.Format_RGB888)
        pix_Red = QPixmap.fromImage(qImg)

        # Format is RGB
        bytesPerLine = 3*width            
        arrCombined = np.require(imgOut_Blue, np.uint8, 'C')
        qImg = QImage(arrCombined.data, width, height, bytesPerLine, QImage.Format_RGB888)
        pix_Blue = QPixmap.fromImage(qImg)

        # Format is RGB
        bytesPerLine = 3*width            
        arrCombined = np.require(imgOut_NIR, np.uint8, 'C')
        qImg = QImage(arrCombined.data, width, height, bytesPerLine, QImage.Format_RGB888)
        pix_NIR = QPixmap.fromImage(qImg)

        return pix_Merged, pix_Red, pix_Blue, pix_NIR

    def processTissue(self, LED_ID, channelEnabled, datasetImages, imageIndex):
            if channelEnabled == False:
                print('channel not enabled')
                return
            
            if LED_ID == 0:
                print('Blue LED')
                reconstructionMethod = self._blueChannelDisplaySettings.displayMode
                imageMinimum = self._blueChannelDisplaySettings.minValue
                imageMaximum = self._blueChannelDisplaySettings.maxValue
                subtractBackground = self._blueChannelDisplaySettings.subtractBackground
                normaliseByLightfield = self._blueChannelDisplaySettings.normaliseByLightfield
                drkFieldImage = self._imgBackgroundBlue
            elif LED_ID == 1:
                print('Red LED')
                reconstructionMethod = self._RedChannelDisplaySettings.displayMode
                imageMinimum = self._RedChannelDisplaySettings.minValue
                imageMaximum = self._RedChannelDisplaySettings.maxValue
                subtractBackground = self._RedChannelDisplaySettings.subtractBackground
                normaliseByLightfield = self._RedChannelDisplaySettings.normaliseByLightfield
                drkFieldImage = self._imgBackgroundBlue # NEEDS TO BE CHANGED LATER
            elif LED_ID == 2:
                print('NIR LED')
                reconstructionMethod = self._NIRChannelDisplaySettings.displayMode
                imageMinimum = self._NIRChannelDisplaySettings.minValue
                imageMaximum = self._NIRChannelDisplaySettings.maxValue
                subtractBackground = self._NIRChannelDisplaySettings.subtractBackground
                normaliseByLightfield = self._NIRChannelDisplaySettings.normaliseByLightfield
                drkFieldImage = self._imgBackgroundBlue # NEEDS TO BE CHANGED LATER
            # else:
            #     print('No LED enabled')
            #     return np.zeros((self._imageHeightProcessing, self._imageWidthProcessing))

            #get combined image 
                #check if led is displayed
                #check if led is enables

                #loop over each LED and process them 


            
                
            

            print('image read')
            im_output = cv2.imread(f'{self._selectedDataset}/{datasetImages[imageIndex]}', 0).astype(np.float32)

            
            #remove offset
            if subtractBackground:
                im_output = cv2.subtract(im_output, drkFieldImage)     #THIS NEED TO BE FOR EACH LED

            #normalise
            if normaliseByLightfield:
                im_output = cv2.divide(im_output, self.im_denom)

            # self.binary_image = self.binary_image.astype(np.uint8)

            
            im_div_masked = cv2.bitwise_and(im_output,im_output,mask = self.im_denom_masked)


            self.average_cores(self.core_arr_vals, self.core_arr_vals_bool, self.idxpts, im_div_masked, self.core_arr_x, self.core_arr_y, self.num_cores)

            nzarry, nzarrx = np.nonzero(im_div_masked)
            values_known = im_div_masked[nzarry,nzarrx]   

            print(f'method: {self.reconstructionMethod}')


            if reconstructionMethod == 1: 
                print('no method chosen')
                im_output = im_output

            elif reconstructionMethod == 2: #"Gaussian":
                print('using Gaussian')
                im_output = cv2.GaussianBlur(src = im_output, ksize = (int(self.kernalSizeGauss), int(self.kernalSizeGauss)), sigmaX = self.gaussianKernelSigma, sigmaY = self.gaussianKernelSigma, borderType = cv2.BORDER_CONSTANT)

            elif reconstructionMethod == 3: #"InterpolationOld"
                print('using old interp')
                im_output = M2.LinearInterpolation_OLD(nzarrx, nzarry, values_known, self.Xi, self.Yi)
                im_output *= 255


            elif reconstructionMethod == 4: #"Interpolation":
                print('using new interp')
                np_im_input_fast_interpolate = M2.interpolate(values_known.flatten(), self.vtx, self.wts)
                im_output = np_im_input_fast_interpolate.reshape(self.m,self.n)
                im_output *= 255

            
            im_output = im_output.astype(np.uint8)


            # if self._blueChannelDisplaySettings.autocontrast:
            im_output = CF.AdjustContrastImage(im_output, imageMinimum, imageMaximum)

            return im_output




            


