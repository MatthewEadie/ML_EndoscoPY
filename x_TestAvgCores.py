import numpy as np
import cv2    
from scipy.ndimage import label
from utils import commonFunctions as CF

class processing():
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
        return im

if __name__ == '__main__':
    proc = processing()
    #Read fibre bundle
    fibre = cv2.imread('fibreMask256.png',0)

    #Pre process fibre bundle
    proc.preprocessFibre(fibre)

    #Read image
    image = cv2.imread('HR.png',0)


    cv2.imshow('image', image)

    #Multiply image with fiber
    imageOverlayed = image * fibre 

    cv2.imshow('overlayed', imageOverlayed)

    #Average cores
    output = proc.averageCores(imageOverlayed)

    cv2.imshow('Output', output)
    cv2.waitKey(0)