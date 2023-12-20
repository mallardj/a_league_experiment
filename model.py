import tensorflow as tf
import numpy as np

def embedding_model():
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Embedding(1000, 64, input_length=10))
    # The model will take as input an integer matrix of size (batch,
    # input_length), and the largest integer (i.e. word index) in the input
    # should be no larger than 999 (vocabulary size).
    # Now model.output_shape is (None, 10, 64), where `None` is the batch
    # dimension.
    input_array = np.random.randint(1000, size=(32, 10))
    model.compile('rmsprop', 'mse')
    output_array = model.predict(input_array)
