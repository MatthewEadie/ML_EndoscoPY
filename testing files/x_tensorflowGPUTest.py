import tensorflow as tf

print(tf.config.list_physical_devices('GPU'))

path = "ML_Models/SIAE_trained500"

modelML = tf.keras.models.load_model(path, compile=False)
modelML.compile(optimizer='adam',loss='mse')
print('model loaded')

#Get shape of input layer
firstLayerShape = modelML.layers[0].input_shape[0]
print('First layer')

print(tf.__version__)