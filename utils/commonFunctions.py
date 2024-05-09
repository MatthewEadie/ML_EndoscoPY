from cv2 import subtract, threshold, divide, bitwise_and, THRESH_BINARY, medianBlur, imshow, convertScaleAbs, cvtColor, COLOR_BGR2GRAY, calcHist
from numpy import uint8, float32, arange, set_printoptions, inf, median
from scipy.ndimage import value_indices
from math import floor
# set_printoptions(threshold=inf)


def subtract_image(image1, image2):
    output = subtract(image1, image2)
    return output


def threshold_image(image):
    minimum_thres = 38
    image = image.astype(uint8)
    ret, binary_image = threshold(image, minimum_thres, 255, THRESH_BINARY)
    return binary_image


def divide_image(image1, image2):
    image2 = image2.astype(float32)
    im_div = divide(image1, image2)
    return im_div


def mask(image1, binary_image):
    im_div_masked = bitwise_and(image1,image1,mask = binary_image)
    return im_div_masked



def core_locations(labeled_arr, num_cores, core_pixel_num, core_arr_x,core_arr_y,core_arr_vals_bool):
    val_indices = list(value_indices(labeled_arr, ignore_value=0).values())

    # # print(val_indices)

    x_list = list(list(zip(*val_indices))[1])
    y_list = list(list(zip(*val_indices))[0])

    for kk in range(1,num_cores+1):
        idx1 = arange(core_pixel_num[kk])
        core_arr_x[kk,0:core_pixel_num[kk]] = x_list[kk-1]
        core_arr_y[kk,0:core_pixel_num[kk]] = y_list[kk-1]
        core_arr_vals_bool[kk,idx1] = True

    return core_arr_x, core_arr_y, core_arr_vals_bool




def core_locations_with_Centroids(labeled_arr, num_cores, core_pixel_num, core_arr_x,core_arr_y,core_arr_vals_bool,xPoints,yPoints):
    val_indices = list(value_indices(labeled_arr, ignore_value=0).values())

    # # print(val_indices)

    x_list = list(list(zip(*val_indices))[1])
    y_list = list(list(zip(*val_indices))[0])

    for kk in range(1,num_cores+1):
        idx1 = arange(core_pixel_num[kk])
        core_arr_x[kk,0:core_pixel_num[kk]] = x_list[kk-1]
        core_arr_y[kk,0:core_pixel_num[kk]] = y_list[kk-1]

        core_arr_vals_bool[kk,idx1] = True

        xPoints[kk-1] = floor(median(x_list[kk-1]))
        yPoints[kk-1] = floor(median(y_list[kk-1]))

    return core_arr_x, core_arr_y, core_arr_vals_bool, xPoints, yPoints




def computeBinaryFibreMask(inputImageLtfldMinBkg, medianFilterSize):
        #https://scikit-image.org/docs/dev/user_guide/data_types.html
    #image is required in BGR format but is read in as RGB
    # u8_inputImage = img_as_ubyte(inputImageLtfldMinBkg/256)

    medianFiltered = medianBlur((inputImageLtfldMinBkg).astype('uint8'), medianFilterSize)


    #cv2.imshow("medianFiltered_PYTHON", medianFiltered)

    #Should be 2 for high intensity, 3 for low intensity
    minimumThresh = 1 #threshold_minimum(medianFiltered,255) 

    ret, medianFilteredBinary = threshold(medianFiltered, 0, 255, THRESH_BINARY)

    binaryFibreMask = medianFilteredBinary.astype(float32)
    binaryFibreMask /= 255

    print(binaryFibreMask)

    return binaryFibreMask

def AdjustContrastImage(image, min, max):
    darkest = min
    brightest = max
    newvalue = (image - darkest)*int(256/(brightest-darkest))

    return newvalue




#https://stackoverflow.com/questions/56905592/automatic-contrast-and-brightness-adjustment-of-a-color-photo-of-a-sheet-of-pape
# Automatic brightness and contrast optimization with optional histogram clipping
def automatic_brightness_and_contrast(image, clip_hist_percent=1):
    # gray = cvtColor(image, COLOR_BGR2GRAY)

    image = (image*256).astype('float32')
    
    # Calculate grayscale histogram
    hist = calcHist([image],[0],None,[256],[0,256])
    hist_size = len(hist)
    
    # Calculate cumulative distribution from the histogram
    accumulator = []
    accumulator.append(float(hist[0]))
    for index in range(1, hist_size):
        accumulator.append(accumulator[index -1] + float(hist[index]))
    
    # Locate points to clip
    maximum = accumulator[-1]
    clip_hist_percent *= (maximum/100.0)
    clip_hist_percent /= 2.0
    
    # Locate left cut
    minimum_gray = 0
    while accumulator[minimum_gray] < clip_hist_percent:
        minimum_gray += 1
    
    # Locate right cut
    maximum_gray = hist_size -1
    while accumulator[maximum_gray] >= (maximum - clip_hist_percent):
        maximum_gray -= 1
    
    # Calculate alpha and beta values
    alpha = 255 / (maximum_gray - minimum_gray)
    beta = -minimum_gray * alpha
    
    '''
    # Calculate new histogram with desired range and show histogram 
    new_hist = cv2.calcHist([gray],[0],None,[256],[minimum_gray,maximum_gray])
    plt.plot(hist)
    plt.plot(new_hist)
    plt.xlim([0,256])
    plt.show()
    '''

    auto_result = convertScaleAbs(image, alpha=alpha, beta=beta)
    return (auto_result, alpha, beta)