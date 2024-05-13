import cv2
import numpy as np
import time
from scipy.ndimage import label
from matplotlib import pyplot as plt

from utils import method2 as M2
from utils import commonFunctions as CF


plt.rcParams["figure.figsize"] = (7,7)

int_test = False


def average_cores(core_arr, core_arr_bool, idx, im, core_x, core_y, num_cores):
    # Copy core values from image to core array. The array is initialised to 0 beforehand.
    core_arr_vals[idx,:] = im[core_arr_y[idx,:],core_x[idx,:]]

    # Calculate mean value per core. The boolean array within "where" was preset to be True
    # for array locations where core values are expected and False for array locations where no
    # no value is expected. With optics used, maximum 70-80 pixels per core is expected.
    core_arr_mean = np.mean(core_arr,axis=1,where=core_arr_bool)

    # Remap back to image the means of whole core back into image. For some reason, I could not vectorise 
    # code below, hence the for loop. Trying to figure out the limitations of vectorisation.
    im[core_y[idx,:],core_x[idx,:]] = core_arr_mean[idx, None]


im_darkfld = cv2.imread('./test images/_Dominic test images/Calibration Data/Exposure_25ms/2018-02-27_14-11-21_Background_Blue.tif',0).astype(np.float32)
im_ltfld = cv2.imread('./test images/_Dominic test images/Calibration Data/Exposure_25ms/2018-02-27_14-11-46_Light_Background_Blue.tif',0).astype(np.float32)

if int_test==True:
    im_darkfld = cv2.imread('./test images/Calibration Data/Exposure_25ms/backgroundMid.tif',0).astype(np.float32)
    im_ltfld = cv2.imread('./test images/Calibration Data/Exposure_25ms/lightfieldMid.tif',0).astype(np.float32)

print('Calib images loaded')

im_denom = cv2.subtract(im_ltfld, im_darkfld)
im_denom = im_denom.astype(np.uint8)
minimum_thres = 55 #38
ret, binary_image = cv2.threshold(im_denom, minimum_thres, 255, cv2.THRESH_BINARY)

cv2.imshow('binary image', binary_image)

im_denom_masked = cv2.bitwise_and(im_denom,im_denom,mask = binary_image)

print('Binary mask created')

labeled_array, num_cores = label(im_denom_masked)

# Find non zero values which represent pixels that 
# are not interpolated
nzarry, nzarrx = np.nonzero(im_denom_masked)
values_known = im_denom_masked[nzarry,nzarrx]

# A meshgrid of pixel coordinates
m, n = im_denom_masked.shape[0], im_denom_masked.shape[1]
mi, ni = im_denom_masked.shape[0], im_denom_masked.shape[1]

[X,Y]=[nzarrx, nzarry]
[Xi,Yi]=np.meshgrid(np.arange(0, n, 1), np.arange(0, m, 1))

xy=np.zeros([X.shape[0],2])
xy[:,0]=Y.flatten()
xy[:,1]=X.flatten()

uv=np.zeros([Xi.shape[0]*Xi.shape[1],2])
uv[:,0]=Yi.flatten()
uv[:,1]=Xi.flatten()

print('Before interp weights')

vtx, wts = M2.interp_weights(xy, uv)

print('After interp weights')

im_denom = cv2.subtract(im_ltfld, im_darkfld)

core_pixel_num = np.zeros(shape=(num_cores+1,1),dtype=int)

#Count cores
unique, core_pixel_num = np.unique(labeled_array, return_counts=True)

print('Number of cores counted')
    
# We need an array only of size determined by the maximum number of pixels per core    
max_num_pixels_per_core = np.max(core_pixel_num[1:])
if max_num_pixels_per_core < 10:
    max_num_pixels_per_core = 10
    print('Number of pixels per core appears to be small.')
elif max_num_pixels_per_core >100:
    print('Number of pixels per core appears to be too big.')

core_arr_x = np.zeros(shape=(num_cores+1,max_num_pixels_per_core),dtype=int)
core_arr_y = np.zeros(shape=(num_cores+1,max_num_pixels_per_core),dtype=int)
core_arr_vals = np.zeros(shape=(num_cores+1,max_num_pixels_per_core),dtype=float)
core_arr_vals_bool = np.full((num_cores+1,max_num_pixels_per_core),False,dtype=bool)
core_arr_mean = np.zeros(shape=(num_cores+1,1),dtype=float)
    
#Core locations
core_arr_x, core_arr_y, core_arr_vals_bool = CF.core_locations(labeled_array, num_cores, core_pixel_num, core_arr_x,core_arr_y,core_arr_vals_bool)

print('Obtained core locations')
print('Finish pre processing')


idxpts=np.arange(1,num_cores+1)






#PROCESSING INPUT IMAGE


im_input = cv2.imread("./test images/_Dominic test images/Imaging Data/2018-02-27_14-49-36/2018-02-27_14-49-36_00000.tif", 0).astype(np.float32)

if int_test==True:
    im_input = cv2.imread("./test images/Imaging Data/testing/lungTissueMid.tif", 0).astype(np.float32)

print('Tissue image loaded')
# cv2.imshow('im inout', im_input)


t0=time.time()

#resize

#remove offset
im_numer = cv2.subtract(im_input, im_darkfld)

# cv2.imshow('im numer', im_numer)


#normalise
im_div = cv2.divide(im_numer, im_denom)
im_div_masked = cv2.bitwise_and(im_div,im_div,mask = binary_image)

# cv2.imshow('im div', im_div)
# cv2.imshow('im masked', im_div_masked)

# labeled_array, num_features = label(im_div_masked)

print('Before cores averaged')

ac_0 = time.time()
average_cores(core_arr_vals, core_arr_vals_bool, idxpts, im_div_masked, core_arr_x, core_arr_y, num_cores)
ac_1 = time.time()

print('After cores averaged')

nzarry, nzarrx = np.nonzero(im_div_masked)
values_known = im_div_masked[nzarry,nzarrx]    



#interpolate
int_0 = time.time()
# np_im_input_fast_interpolate = M2.interpolate(values_known.flatten(), vtx, wts)
# imginterp_fast = np_im_input_fast_interpolate.reshape(m,n)
int_1 = time.time()

print('Interpolation complete')


t_g=(time.time()-t0)
print(f'time taken to average cores: {ac_1-ac_0}')
print(f'time taken to interpolate: {int_1-int_0}')
print(f'total time taken: {t_g}')

# ax = plt.gca()
# ax.get_xaxis().set_visible(False)
# ax.get_yaxis().set_visible(False)
# plt.imshow(imginterp_fast,cmap='gray')
# plt.title('einsum image interpolated')
# plt.show()

cv2.waitKey(0)