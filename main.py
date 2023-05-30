# -*- coding: utf-8 -*-
"""main.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1woDq4BfmhYIMUWnd8FAiVDrGNHgXX0mm
"""

import streamlit as st
from process import SolarDataProcessor
from model import TransferLearningModel

# Constants
BASE_MODEL_PATH = "https://github.com/udaybhaskar717/Universal-Solar-Power-Forecasting-Tool/blob/main/Solar_Irradiance_Bi-LSTM_Base_Model_kaz.h5
TARGET_REGIONS = ['']  # replace with actual target regions
N_TIMESTEPS = 96
N_FEATURES = 26
N_OUTPUTS = 1

# Load data
data = pd.read_csv("your_file_path")  # replace with your actual data file path

# Sidebar: User inputs
st.sidebar.header('User Input Parameters')
train_start = st.sidebar.text_input('Train start datetime', "2022-07-31T00:00:00Z")
train_end = st.sidebar.text_input('Train end datetime', "2022-12-31T23:45:00Z")
test_start = st.sidebar.text_input('Test start datetime', "2022-12-31T23:45:00Z")
strategy = st.sidebar.selectbox('Transfer learning strategy', ['S1', 'S2', 'S3'])
epochs = st.sidebar.number_input('Number of epochs', 1, 500, 250)

# Preprocess data
solar_data_processor = SolarDataProcessor(data, N_TIMESTEPS, N_OUTPUTS, only_production=False, train_start=train_start, train_end=train_end, test_start=test_start)
X_train, y_train, X_test, y_test = solar_data_processor.get_processed_data()

# Transfer learning model
tl_model = TransferLearningModel(BASE_MODEL_PATH, TARGET_REGIONS, N_TIMESTEPS, N_FEATURES, N_OUTPUTS, strategy, epochs)
tl_model.compile_model()

# Train model
tl_model.fit_model(X_train, y_train, X_test, y_test)  # assuming X_test, y_test are validation data

# Predict
predictions = tl_model.predict(X_test)

# Show predictions
st.header('Predictions')
st.write(predictions)