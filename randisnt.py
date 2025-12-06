import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime
import os
import sys
import logging
import joblib

# Ethan Dykes

# RANDOM NUMBERS ARENT
# The goal of this project is to prove if an AI model is capable of guessing the next numbers in a chain.
# Utilizes Keras to create an LSTM AI model, allowing Neural Networks to calculate algorithms over training on numbers
# Trains on a chain of random numbers, and then predicts off of a testing split.
# Built to train on custom hardware, but modifed for hardware Agnostic training

# TRAINING VARIABLES
# These are the global variables for training

# Input sequence length
SEQUENCE_LENGTH = 256
NUM_FEATURES = 1
# Numbers being trained on
PRNG_SEQUENCE_LENGTH = 1024
# Predicted values: for most effectiveness using 0-9
PRED_VALUES = 10
# How many to predict
PRED_RANGE = 32
# How many times are we training? (Epochs)
PASSES = 10
# Batch size for training
GLOBAL_BATCH_SIZE = 64
# Seed PRNG, for testing purposes, preseeds PRNG for expected known results
RANDOM_SEED = 42 # 42 lol, for some reason this is classic for AI researchers. Its almost everywhere in AI docs



# OPTIONAL VARIABLES

# make FALSE if training on CPU
GPU_ENABLED = True
# Logging?
LOGGING = True
# Logging file
OUTPUT_LOGFILE = "output.txt"
# Save model after training
SAVE_MODEL = False
# Saved model name
MODEL_NAME = "randisnt.keras"
# Save scaler after training
SAVE_SCALER = False
# Saved Scaler name
SCALER_NAME = "scaler.save"


# preseeding PRNG for debugging outputs.
np.random.seed(RANDOM_SEED)

# Logging setup
if LOGGING:
        logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s %(message)s",handlers=[logging.StreamHandler(sys.stdout),logging.FileHandler(OUTPUT_LOGFILE, mode="a")])
        logger = logging.getLogger(__name__)

# Data generation: integers 0-9
def generate_data(total=PRNG_SEQUENCE_LENGTH, value_range=PRED_VALUES):
        # generates Ints, but saves them as floats
        data = np.random.randint(0,value_range, size=(total)).astype(np.float32)
        # Why? Keras cant train on Integers, and requires discrete values
        # this error is also why earlier versions run on numpy float values, this was an error I couldnt get around at first
        # easy fix after all
        return data.reshape(-1,1)

# Window Function: controls the hardware training window
def create_sequences(data, seq_len, pred_range):
        x, y = [], []
        max_i = len(data) - seq_len - pred_range + 1
        for i in range(max_i):
                x.append(data[i:(i + seq_len), 0])
                y.append(data[i + seq_len: i + seq_len + pred_range, 0])
        return np.array(x), np.array(y)

# AI Model creation
def build_model(seq_len, num_features, pred_len):
        # model = Sequential([Input(shape=(seq_len,num_features)),LSTM(64, return_sequences=False),Dense(pred_len)])
        model = Sequential()
        model.add(LSTM(units=50, return_sequences=False, input_shape=(SEQUENCE_LENGTH, NUM_FEATURES)))
        model.add(Dense(PRED_RANGE))
        model.compile(optimizer="adam",loss="mse")
        # model.summary()
        return model

# TRAINING
def train_model():
        startTime = datetime.now()
        logger.info("Starting Training")

        data = generate_data(total=PRNG_SEQUENCE_LENGTH,value_range=PRED_VALUES)
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled = scaler.fit_transform(data)
        logger.info("Generated Raw Data")

        # Sequences
        X, y = create_sequences(scaled, SEQUENCE_LENGTH, PRED_RANGE)

        X = X.reshape(X.shape[0], SEQUENCE_LENGTH, NUM_FEATURES)
        y = y.reshape(y.shape[0], PRED_RANGE)
        logger.info("X Shape: %s, y shape: %s", X.shape, y.shape)

        # Training Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_SEED)

        logger.info("Train Size: %d, Test size: %d", X_train.shape[0], X_test.shape[0])

        # Training Strategy
        # Runs check on whether or not GPU training is enabled
        if GPU_ENABLED:
                os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"
                logger.info("Using GPU devices")
                strategy = tf.distribute.MirroredStrategy()
        # When training on multiple processors, needs to mirror model to each one
                with strategy.scope():
                        # model = build_model(SEQUENCE_LENGTH, NUM_FEATURES, PRED_RANGE)
                        model = Sequential()
                        model.add(LSTM(units=50, return_sequences=False, input_shape=(SEQUENCE_LENGTH, NUM_FEATURES)))
                        model.add(Dense(PRED_RANGE))
                        model.compile(optimizer="adam",loss="mse")

        else:
                os.environ["CUDA_VISIBLE_DEVICES"] = ""
                logger.info("Using CPU (WARNING: NOT OPTIMIZED FOR CPU TRAINING)")
                strategy = None
                model = build_model(SEQUENCE_LENGTH, NUM_FEATURES, PRED_RANGE)

        model.summary(print_fn=lambda s: logger.info(s))

        logger.info("Starting training for %d Epochs", PASSES)


        # Train model
        # history = model.fit(train_ds, epochs=PASSES, validation_data=val_ds, verbose=1)
        history = model.fit(X_train, y_train,epochs=PASSES,batch_size=GLOBAL_BATCH_SIZE,validation_split=0.2,verbose=1)

# 1 talley mark per hour lost trying to run validation data for training: l l l l l l
        logger.info("Training Complete")

        # saving model
        if SAVE_MODEL:
                model.save(MODEL_NAME)
                logger.info("Model saved to %s", MODEL_NAME)

        # saving scaler
        if SAVE_SCALER:
                joblib.dump(scaler, SCALER_NAME)
                logger.info("Scaler saved to %s", SCALER_NAME)
        # recording training history
        endTime = datetime.now()
        duration = endTime-startTime
        # logging.info("Training Complete. Trained from %s to $s", str(startTime), str(endTime))
        logging.info("Training Complete. Training start: %s ", str(startTime))
        logging.info("Total Training Duration: %s", str(duration))

        return {"model": model,"scaler": scaler,"X_test": X_test,"y_test": y_test,"strategy": strategy}


# PREDICTION
def predict(model, scaler, X_test, y_test, strategy=None):
        num_replicas = strategy.num_replicas_in_sync
        test_input = X_test[0:1]
        predicted_scaled = None
        logger.info("Beginning Prediction")
        if test_input.shape[0] < num_replicas:
                # replicate the single sample so each replica receives at least one item
                test_input_rep = np.repeat(test_input, num_replicas, axis=0)  # shape (num_replicas, seq_len, features)
                predicted_scaled = model.predict(test_input_rep, batch_size=num_replicas)
                # take the first prediction as the real one (they're identical because inputs were duplicated)
                predicted_scaled = predicted_scaled[0:1]
        else:
                predicted_scaled = model.predict(test_input, batch_size=num_replicas)
        predicted_number = scaler.inverse_transform(predicted_scaled)
        actual_number = scaler.inverse_transform(y_test[0:1])

        summary = {"predicted_first": float(predicted_number[0,0]), "actual_first": float(actual_number[0,0]),"passes":PASSES,"train_size":int(len(X_test)),"test_size":int(len(y_test)) }

        logger.info("Prediction: predicted=%s actual=%s",predicted_number.ravel().tolist(),actual_number.ravel().tolist())

        logger.info("Summary: %s", summary)
        return summary

# MAIN
# Where everything runs
def main():
        training = train_model()
        summary = predict(model=training["model"],scaler=training["scaler"],X_test=training["X_test"],y_test=training["y_test"],strategy=training["strategy"])

if __name__ == "__main__":
        main()


# Powered by the Ballmer Peak
