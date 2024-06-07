import numpy as np

import cv2 as cv

# ROTATE STACK CHANNELS
image1 = cv.imread('small images/1.png',0)
image2 = cv.imread('small images/2.png',0)
image3 = cv.imread('small images/3.png',0)

print(image1.shape)

stack = np.zeros((10,10,3))

stack[0,:,:,0] = image1
stack[0,:,:,1] = image2
stack[0,:,:,2] = image3

print(stack.shape)


cv.imshow('image 1', stack[:,:,0])
cv.imshow('image 2', stack[:,:,1])
cv.imshow('image 3', stack[:,:,2])
cv.waitKey(0)

stack = np.roll(stack, -1)

cv.imshow('image 1', stack[:,:,0])
cv.imshow('image 2', stack[:,:,1])
cv.imshow('image 3', stack[:,:,2])
cv.waitKey(0)

# import numpy as np 
   
# zeros = np.zeros((2,2))
# ones = np.ones((2,2))
# twos = np.zeros((2,2)) + 2

# array = np.zeros((2,2,3))
# array[:,:,0] = zeros
# array[:,:,1] = ones
# array[:,:,2] = twos

# print(array.shape)
# print("Original array : \n", array) 
# print()
# print("Zeroth item : \n", array[:,:,0])
# print()

# # flatStack = array.flatten()
# stack = np.roll(array, -1)
# # stack = stack.reshape(2,2,3)
# print(stack)
# print()
# print(stack[:,:,0])

# stack = np.roll(array, [-1, 1, 1], axis=(1, 0, 0))

# print("Rolled array : \n", stack) 
# print("New zeroth item : \n", stack[:,:,0])


# ROTATE STACK 4TH DIMENSION
# image1 = cv.imread('small images/1.png')
# image2 = cv.imread('small images/2.png')
# image3 = cv.imread('small images/3.png')

# stack = np.zeros((3,10,10,3))

# stack[0,:,:,:] = image1
# stack[1,:,:,:] = image2
# stack[2,:,:,:] = image3


# cv.imshow('image 1', stack[0])
# cv.imshow('image 2', stack[1])
# cv.imshow('image 3', stack[2])
# cv.waitKey(0)

# stack = np.roll(stack, [0, 0, 0, -1], axis=(1, 0, 0, 0))

# cv.imshow('image 1', stack[0])
# cv.imshow('image 2', stack[1])
# cv.imshow('image 3', stack[2])
# cv.waitKey(0)

# from datetime import datetime

# now = datetime.now()
# dateTime = now.strftime("%H-%M-%S_%d-%m-%Y")

# print(dateTime)


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