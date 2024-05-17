import tensorflow as tf

print(tf.config.list_physical_devices('GPU'))

path = "./MFAE_Models/MFUNet_trained500_11"

modelML = tf.keras.models.load_model(path, compile=False)
modelML.compile(optimizer='adam',loss='mse')
print('model loaded')

#Get shape of input layer
firstLayerShape = modelML.layers[0].input_shape[0]
print('First layer')

