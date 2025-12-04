#!/usr/bin/env python3
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime
import os
import sys

# train AI model on dual GPU setup via CUDA
# sets up an NP array of random numbers, set by the parameters
# Retrains on data, then at the end makes predictions

# Set environment variable to ensure TensorFlow sees the 2 GPUs
os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"

# set logging start time
startTime = datetime.now()

# Define Mirrored Strategy
strategy = tf.distribute.MirroredStrategy()
print(f'Number of devices being used: {strategy.num_replicas_in_sync}')

# Parameter setting
SEQUENCE_LENGTH = 256
NUM_FEATURES = 1
PRNG_SEQUENCE_LENGTH = 512
PRED_RANGE = 10
PASSES = 10

# Batch Size: doubled from normal for dual GPU training
GLOBAL_BATCH_SIZE = 64

# PRNG sample data
np.random.seed(42)
raw_data = np.random.rand(PRNG_SEQUENCE_LENGTH)
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(raw_data.reshape(-1, 1))

# Input/Output Sequences
def create_sequences(data, seq_len, pred_range):
    x, y = [], []
    for i in range(len(data) - seq_len - pred_range + 1):
        x.append(data[i:(i + seq_len), 0])
        y.append(data[i + seq_len: i + seq_len + pred_range, 0])
    return np.array(x), np.array(y)

# Create sequences
X, y = create_sequences(scaled_data, SEQUENCE_LENGTH, PRED_RANGE)
# If no sequences were created this will raise (shape[0] == 0)
if X.size == 0 or y.size == 0:
    raise ValueError(
        f"Sequence length {SEQUENCE_LENGTH} is too large for dataset "
        f"({PRNG_SEQUENCE_LENGTH} values). No sequences could be created."
    )

# reshape for LSTM
X = X.reshape(X.shape[0], X.shape[1], NUM_FEATURES)
y = y.reshape(y.shape[0], PRED_RANGE)

# Debug pring for x and y shapes
print("X shape:", X.shape, "y shape:", y.shape)

# ensure train/test split won't produce an empty test set
min_test_size = 1
computed_test_size = int(0.2 * len(X))
if computed_test_size < min_test_size:
    raise ValueError(
        f"Test split would be empty (computed size {computed_test_size}). "
        f"Reduce SEQUENCE_LENGTH or increase PRNG_SEQUENCE_LENGTH."
    )

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Train size:", X_train.shape[0], "Test size:", X_test.shape[0])

# Build LSTM model inside strategy scope
with strategy.scope():
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=False, input_shape=(SEQUENCE_LENGTH, NUM_FEATURES)))
    model.add(Dense(PRED_RANGE))

    # Compile Model
    model.compile(optimizer='adam', loss='mean_squared_error')

print("Starting GPU model training...")

# Train the Model
history = model.fit(
    X_train, y_train,
    epochs=PASSES,
    batch_size=GLOBAL_BATCH_SIZE,
    validation_data=(X_test, y_test),
    verbose=1
)

print("Training Complete")

# PREDICTION MODE:
num_replicas = strategy.num_replicas_in_sync
test_input = X_test[0:1]

if test_input.shape[0] == 0:
    raise ValueError("test_input is empty. Cannot predict.")

if test_input.shape[0] < num_replicas:
    # replicate the single sample so each replica receives at least one item
    test_input_rep = np.repeat(test_input, num_replicas, axis=0)  # shape (num_replicas, seq_len, features)
    predicted_scaled = model.predict(test_input_rep, batch_size=num_replicas)
    # take the first prediction as the real one (they're identical because inputs were duplicated)
    predicted_scaled = predicted_scaled[0:1]
else:
    predicted_scaled = model.predict(test_input, batch_size=num_replicas)

predicted_number = scaler.inverse_transform(predicted_scaled)
actual_scaled = y_test[0:1]
actual_number = scaler.inverse_transform(actual_scaled)

# Final time recording for logging output
endTime = datetime.now()

# output
print(f"Training results for training from", startTime, " to ", endTime)
print(f"\nPredicted Next Number: {predicted_number[0,0]:.1f}")
print(f"Actual Next Number:    {actual_number[0,0]:.1f}")
print(f"Training Passes: {PASSES}")
# Logging output
o = sys.stdout
with open('output.txt', 'a') as f:
    sys.stdout = f
    print(f"Training results for training from", startTime, " to ", endTime)
    print(f"Predicted Next Number: {predicted_number[0,0]:.1f}")
    print(f"Actual Next Number:    {actual_number[0,0]:.1f}")
    print(f"Training Passes: {PASSES}")
sys.stdout = o
