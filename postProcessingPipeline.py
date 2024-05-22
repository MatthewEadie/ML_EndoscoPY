import numpy as np
import cv2

import os

from scipy.ndimage import label
from matplotlib import pyplot as plt

from utils import method2 as M2
from utils import method1 as M1
from utils import commonFunctions as CF


from PyQt5.QtCore import *
from PyQt5.QtGui import QImage, QPixmap




class playbackMethod(QObject):
   


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




            


