# import tensorflow as tf

# import numpy as np
# import matplotlib.pyplot as plt
# import os
# # from keras.saving import  #kersa now no longer dependant on tensorflow
# from cv2 import imshow, imwrite, waitKey
# from math import floor
# import time




# #----------
# # Settings
# channels = 11
# model_fp = "ML_Models\MFUNet_trained500_11"
# test_index = 3 #index of image to test model on
# path_datasets = "./image_stacks"
# save_path = "image_stacks/" + str(channels) 
# #----------


# currentImageNum = 0
# imageStack = np.zeros((1,256,256,3))

# dataset = np.load(os.path.join(path_datasets, "X_test4D.npy"))

# imageStack = dataset[currentImageNum:currentImageNum+1,:,:,:]

# print(imageStack.shape)

# modelML = tf.keras.models.load_model(model_fp,compile=False)
# modelML.compile(optimizer='adam',loss='mse')

# firstLayerShape = modelML.layers[0].input_shape[0]
# print(firstLayerShape)

# X_pred = modelML(imageStack)

# # pred_output = X_pred[0,:,:,0].numpy()
# # pred_output *= 255
# # pred_output[pred_output>255] = 255

# # plt.imshow(pred_output[0,:,:,0])
# # plt.show



# # #Load testing datasets
# # X_test = np.load(os.path.join(path_datasets, "X_test1D.npy")) #(32,256,256,4) Images to run through model
# # Y_test = np.load(os.path.join(path_datasets, "Y_test1D.npy")) #(32,256,256,4) HR images for comparison

# # #Load trained model
# # MF_UNet = tf.keras.models.load_model(model_fp,compile=False)
# # MF_UNet.compile(optimizer='adam',loss='mse')

# # print(f"Shape of X_test: {X_test.shape}")
# # print(f"Shape of Y_test: {Y_test.shape}")

# # firstLayer = MF_UNet.layers[0].input_shape[0]
# # print(f'First layer: {firstLayer}')
# # print(f'Image number: {firstLayer[0]}')
# # print(f'X axis shape: {firstLayer[1]}')
# # print(f'Y axis shape: {firstLayer[2]}')
# # print(f'Channel shape: {firstLayer[3]}')

# # test_image = X_test[0:1]

# # X_pred = MF_UNet(test_image)

# # fig, ax = plt.subplots(3)
# # ax[0].imshow(X_test[0,:,:,0])
# # ax[0].set_title('LR')

# # ax[1].imshow(X_pred[0,:,:,0])
# # ax[1].set_title('Prediction')

# # ax[2].imshow(Y_test[0])
# # ax[2].set_title('HR')

# # plt.show()

# # plt.imshow(X_pred[0,:,:,0])
# # plt.show

# # imshow('Output',X_pred[0,:,:,0])
# # waitKey(0)



"""
    Created by: Matthew Eadie
    Date: 10/01/22

    Work based off RAMS multiframe super resolution 
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import tensorflow as tf
from cv2 import imwrite

#----------
# Settings
model_fp = "ML_Models\SIAE_trained500_old"
test_index = 30 #index of image to test model on
path_datasets = "image_stacks"
save_path = "SR_1DImages"
#----------



load_datasets = True
test_model = True
reconstruct_dataset = False

if(load_datasets):
    X_test = np.load(os.path.join(path_datasets, "X_test1D.npy")) #(32,256,256,4) Images to run through model
    Y_test = np.load(os.path.join(path_datasets, "Y_test1D.npy")) #(32,256,256,4) HR images for comparison

    MF_UNet = tf.keras.models.load_model(model_fp,compile=False)
    MF_UNet.compile(optimizer='adam',loss='mse')

    print(f"Shape of X_test: {X_test.shape}")
    print(f"Shape of Y_test: {Y_test.shape}")



if(test_model):
    test_image = X_test[test_index:test_index+1]

    print(f"Shape of test_image: {test_image.shape}")

    X_pred = MF_UNet(test_image)

    fig, ax = plt.subplots(1,3)
    ax[0].imshow(X_test[test_index], cmap = 'gray')
    ax[0].set_title('LR')

    ax[1].imshow(X_pred[0,:,:,0], cmap ='gray')
    ax[1].set_title('Prediction')

    ax[2].imshow(Y_test[test_index], cmap = 'gray')
    ax[2].set_title('HR')
    
    plt.show()



if(reconstruct_dataset):
    if not os.path.isdir(save_path):
        os.mkdir(save_path)

    for index in range(X_test.shape[0]):
        test_image = X_test[index:index+1]
        X_pred = MF_UNet(test_image)

        plt.imsave(save_path + "/SR{}.png".format(index), X_pred[0,:,:,0], cmap = 'gray')