import numpy as np

import cv2 as cv

image1 = cv.imread('small images/1.png')
image2 = cv.imread('small images/2.png')
image3 = cv.imread('small images/3.png')

stack = np.zeros((3,10,10,3))

stack[0] = image1
stack[1] = image2
stack[2] = image3


# cv.imshow('image 1', stack[0])
# cv.imshow('image 2', stack[1])
# cv.imshow('image 3', stack[2])
# cv.waitKey(0)

stack = np.roll(stack, [0, 0, 0, -1], axis=(1, 0, 0, 0))

# cv.imshow('image 1', stack[0])
# cv.imshow('image 2', stack[1])
# cv.imshow('image 3', stack[2])
# cv.waitKey(0)

from datetime import datetime

now = datetime.now()
dateTime = now.strftime("%H-%M-%S_%d-%m-%Y")

print(dateTime)


# x = np.zeros((5,2,2,2))
# x[0,:,:,:] = 1
# x[1,:,:,:] = 2
# x[2,:,:,:] = 3
# x[3,:,:,:] = 4
# x[4,:,:,:] = 5



# print(x)
# print()

# x = np.roll(x, [0, 0, 0, -1], axis=(1, 0, 0, 0))
# print('New Array')
# print(x)