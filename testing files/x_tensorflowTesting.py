import tensorflow as tf

import numpy as np
import matplotlib.pyplot as plt
import os
# from keras.saving import  #kersa now no longer dependant on tensorflow
from cv2 import imshow, imwrite, waitKey
from math import floor
import time




#----------
# Settings
channels = 11
model_fp = "MFAE_Models/MFUNet_trained500_" + str(channels) 
test_index = 3 #index of image to test model on
path_datasets = "test images/image_stacks"
save_path = "image_stacks/" + str(channels) 
#----------




#Load testing datasets
X_test = np.load(os.path.join(path_datasets, "X_test4D.npy")) #(32,256,256,4) Images to run through model
Y_test = np.load(os.path.join(path_datasets, "Y_test4D.npy")) #(32,256,256,4) HR images for comparison

#Load trained model
MF_UNet = tf.keras.models.load_model(model_fp,compile=False)
MF_UNet.compile(optimizer='adam',loss='mse')

print(f"Shape of X_test: {X_test.shape}")
print(f"Shape of Y_test: {Y_test.shape}")


test_image = X_test[0:1]

X_pred = MF_UNet(test_image)

# fig, ax = plt.subplots(3)
# ax[0].imshow(X_test[0,:,:,0])
# ax[0].set_title('LR')

# ax[1].imshow(X_pred[0,:,:,0])
# ax[1].set_title('Prediction')

# ax[2].imshow(Y_test[0])
# ax[2].set_title('HR')

# plt.show()

plt.imshow(X_pred[0,:,:,0])
plt.show

# imshow('Output',X_pred[0,:,:,0])
# waitKey(0)