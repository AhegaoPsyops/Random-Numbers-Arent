#!/usr/bin/env python3
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import os

# DESCRIPTION
# LSTM AI model using Keras to generate a chain of pre-seeded random numbers, train, and the predict off the next lines of numbers. 
# Setup to work on a Dual GPU environment, if you dont have 2 NVIDIA GPUs and CUDA, it wont work. 
# Breaks during the prediction phase. 


# Whats going on?
# train AI model on dual GPU setup via CUDA
# sets up an NP array of random numbers, set by the parameters
# Retrains on data, then at the end makes predictions
# mostly hijacked from various Keras Docs
# still learning how it works, fails during the prediction setting

# Set environment variable to ensure TensorFlow sees the 2 GPUs
os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"

# Define Mirrored Strategy
strategy = tf.distribute.MirroredStrategy()
print(f'Number of devices being used: {strategy.num_replicas_in_sync}')

# Parameter setting
SEQUENCE_LENGTH = 256
NUM_FEATURES = 1
# Breaks if any longer length
PRNG_SEQUENCE_LENGTH = 100000
PRED_RANGE = 1

# Batch Size: doubled from normal for dual GPU training
GLOBAL_BATCH_SIZE = 64

# PRNG sample data
np.random.seed(42)
raw_data = np.random.rand(PRNG_SEQUENCE_LENGTH)
scaler = MinMaxScaler(feature_range=(0,1))
scaled_data = scaler.fit_transform(raw_data.reshape(-1,1))

# Input/Output Sequences
def create_sequences(data, seq_len, pred_range):
        x, y = [],[]
        for i in range(len(data) - seq_len - pred_range + 1):
                x.append(data[i:(i + seq_len), 0])
                y.append(data[i + seq_len : i + seq_len + pred_range, 0 ])
        return np.array(x), np.array(y)
X, y = create_sequences(scaled_data, SEQUENCE_LENGTH, PRED_RANGE)
X = X.reshape(X.shape[0], X.shape[1], NUM_FEATURES)
y = y.reshape(y.shape[0], PRED_RANGE)

X_train, X_test, y_train, y_test = train_test_split(X,y, test_size = 0.2,>


# Build LSTM model
with strategy.scope():
        model = Sequential()
        model.add(LSTM(units=50,return_sequences=False, input_shape=(SEQU>
        model.add(Dense(PRED_RANGE))

# Compile Model
        model.compile(optimizer='adam', loss = 'mean_squared_error')

print("Starting GPU model training...")

# Train the Model
# can change epochs as needed
history = model.fit(X_train, y_train,epochs=10,batch_size=GLOBAL_BATCH_SI>

print("Training Complete")

# Make predictions (fails here)

test_input = X_test[0].reshape(1, SEQUENCE_LENGTH, NUM_FEATURES)
predicted_scaled = model.predict(test_input)

predicted_number = scalar.inverse_transform(predicted_scaled)
actual_number = model.predict(test_input)
