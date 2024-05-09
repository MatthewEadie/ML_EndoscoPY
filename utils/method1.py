from cv2 import minMaxLoc, calcHist, integral, flip, convertScaleAbs, CV_32FC1
from numpy import amax, zeros, float32
from math import ceil

def adjustContrast(imageInOut, lowerSat, upperSat, fibreMask, nPixels):

    imageMin, imageMax, minLoc, maxLoc = minMaxLoc(imageInOut, fibreMask) #Mask not type int

    #u8_imageInOut = cv2.convertScaleAbs(u8_imageInOut, alpha= 255 / (imageMax - imageMin), beta= -imageMin * 255 / (imageMax - imageMin))

    alpha= 255 / (imageMax - imageMin)
    beta= -imageMin * 255 / (imageMax - imageMin)
    u8_imageInOut = imageInOut * alpha + beta

    u8_imageInOut[u8_imageInOut<0] = 0 # turn negative values to 0
    u8_imageInOut[u8_imageInOut>255] = 255 # turn negative values to 0

    u8_imageInOut = u8_imageInOut / amax(u8_imageInOut)

    histogramSize = [256]
    range = [0, 256]
    fp_hist = zeros((256,1))

    fp_hist = calcHist([u8_imageInOut.astype('uint8')], [0], fibreMask, histSize= histogramSize , ranges= range)



    fp_integHistBottomUp = integral(fp_hist, sdepth= CV_32FC1)
    fp_histFlipped = flip(fp_hist, -1)
    fp_integHistTopDown = integral(fp_histFlipped, sdepth= CV_32FC1)

    calculatedMin, calculatedRange = calcContrastValsFromHist(lowerSat, upperSat, fp_integHistBottomUp, fp_integHistTopDown, nPixels)

    outputImage = convertScaleAbs(u8_imageInOut, alpha=255.0 / calculatedRange, beta= -calculatedMin * 255.0 / calculatedRange)

    return outputImage



def calcContrastValsFromHist(lowerPercentageContrast, upperPercentageContrast, cumsumHistBottomUp, cumsumHistTopDown, nPixels):

    cumsumHistBottomUpPercent = cumsumHistBottomUp / nPixels
    cumsumHistTopDownPercent = cumsumHistTopDown / nPixels

    # variables for lower and upper limit of pixel range in original image
    binLowerChannel = 0
    binUpperChannel = 1 # initialise this with 0 rather than 255, otherwise the image might stay black if no bin is found

    # boolean to remember if lower and upper limits have been found
    binLowerFoundChannel = False
    binUpperFoundChannel = False

    maxIndexHistogram = 255
    currIndex = 0

    MAX_8_BIT_VAL = 255.0

    # create first entries for the cumulative sums of the histograms, both absolute and percent histogram, both bottom-up and top-down directions
    # check if this already satisfies conditions for autocontrast range
    if (cumsumHistBottomUpPercent[1, 1] > lowerPercentageContrast):
        binLowerFoundChannel = True
        binLowerChannel = 0

    if (cumsumHistTopDownPercent[1, 1] > 1.0 - upperPercentageContrast):
        binUpperFoundChannel = True
        binUpperChannel = 255

    # calculate the cumulative sum of pixel values, and check directly if the lower or upper bound for the original range has been found
    for i in range(0, maxIndexHistogram):
        if not (binLowerFoundChannel):
            if (cumsumHistBottomUpPercent[i + 1, 1].astype(float32) >= lowerPercentageContrast):
                binLowerChannel = i; # if the pixels from the bin above the given percentage should be included [in doubt, this saturates a few more pixels than asked for]
                binLowerFoundChannel = True

        if not (binUpperFoundChannel):
            currIndex = maxIndexHistogram - i
            if (cumsumHistTopDownPercent[i + 1, 1] >= 1 - upperPercentageContrast):
                binUpperChannel = currIndex; # if the pixels from the bin above the given percentage should be included  (in doubt, this saturates a few more pixels than asked for)
                binUpperFoundChannel = True

        if (binUpperFoundChannel & binLowerFoundChannel):
            break

    # make sure that the difference between upper and lower limit is greater than zero, adjust the values otherwise (this can happen for example for completely dark images)
    if (binLowerChannel >= binUpperChannel):
        if (binUpperChannel < 255):
            binUpperChannel = binLowerChannel + 1
        
        else:
            binLowerChannel = binUpperChannel - 1

    channelMin = binLowerChannel
    channelRange = binUpperChannel - channelMin

    return channelMin, channelRange

def computeGaussianKernelSizeFromSigma(gaussianKernelSigma):
    if (gaussianKernelSigma > 2):
        # kernel diameter calculation according to https://github.com/opencv/opencv/blob/9c23f2f1a682faa9f0b2c2223a857c7d93ba65a6/modules/imgproc/src/smooth.cpp#L4085
        # where ksize.width and ksize.height = cvRound(sigma1*(depth == CV_8U ? 3 : 4)*2 + 1)|1;
        # we use CV_32F, so ksize.width and ksize.height = cvRound(sigma1 * 8 + 1)|1;

        #OpenCV style kernel size calculation
        kernelDiamCalculatedInt = ceil((gaussianKernelSigma * 8 + 1)) | 1
    
    else:
        #Matlab style kernel size calculation
        kernelDiamCalculatedInt = 2*ceil(2 * gaussianKernelSigma) + 1
    

    #Size kernelSizeGauss(kernelDiamCalculatedInt, kernelDiamCalculatedInt);
    return kernelDiamCalculatedInt


