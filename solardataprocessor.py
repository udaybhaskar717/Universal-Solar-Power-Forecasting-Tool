# -*- coding: utf-8 -*-
"""SolarDataProcessor.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/187CT-9Rrgz_YVF5IzFKUcvGLec_t6V8D
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

class DateTimeConverter:
    def __init__(self, data):
        self.data = data

    def add_month_hour_columns(self):
        self.data['Month'] = pd.to_datetime(self.data['PeriodStart']).dt.month
        self.data['Hour'] = pd.to_datetime(self.data['PeriodStart']).dt.hour

    def add_features(self):
        self.data = pd.get_dummies(self.data, columns=['Month'])
        self.data['sin_hour'] = np.sin(2 * np.pi * self.data['Hour'].astype(int) / 24)
        self.data['cos_hour'] = np.cos(2 * np.pi * self.data['Hour'].astype(int) / 24)

 

    def get_data(self):
        return self.data

class SplitData:
    def __init__(self, data, n_timesteps, n_outputs, train_start, train_end, test_start, only_production=False):
        self.df = data
        self.train = None
        self.test = None
        self.x_train = None
        self.y_train = None
        self.x_test = None
        self.y_test = None
        self.only_production = only_production
        self.lag = n_timesteps
        self.n_features = None
        self.num_of_outputs = n_outputs
        self.cols = self.df.columns
        self.train_start = train_start
        self.train_end = train_end
        self.test_start = test_start

    def split_sequences(self, sequences):
        X, y = list(), list()
        for i in range(len(sequences)):
            end_ix = i + self.lag
            if end_ix > len(sequences):
                break
            if self.only_production:
                seq_x, seq_y = sequences[i:end_ix, -1], sequences[end_ix:(end_ix+self.num_of_outputs), -1]
            else:
                seq_x, seq_y = sequences[i:end_ix, :], sequences[end_ix:(end_ix+self.num_of_outputs),-1]
            X.append(seq_x)
            y.append(seq_y)
        return (np.array(X), np.array(y))

    def unique_shapes(self,x, y, lag_, n_features_, num_of_outputs_, only_production):
        uniuqe_shapes = []
        for k in range(len(x)):
            if only_production==True:
                if (x[k].shape == (lag_,)) & (y[k].shape == (num_of_outputs_,)):
                    uniuqe_shapes.append(k)
            else:
                if (x[k].shape == (lag_, n_features_)) & (y[k].shape == (num_of_outputs_,)):
                    uniuqe_shapes.append(k)       
        x = x[uniuqe_shapes]
        y = y[uniuqe_shapes]
        x = np.stack(x)
        y = np.stack(y)
        return (x, y)
        
    def preprocess_data(self):
        self.n_features = len(self.cols)
        feature_index = self.df.columns.get_loc('Ghi')
        df_feature = self.df.pop('Ghi')
        self.df.insert(len(self.df.columns), 'Ghi', df_feature)
        self.df['PeriodStart'] = pd.to_datetime(self.df['PeriodStart'])
        self.train = self.df[(self.df['PeriodStart'] >= pd.to_datetime(self.train_start)) & (self.df['PeriodStart'] <= pd.to_datetime(self.train_end))]
        self.test = self.df[self.df['PeriodStart'] >= pd.to_datetime(self.test_start)]
        self.x_train, self.y_train = self.split_sequences(self.train.values)
        self.x_test, self.y_test = self.split_sequences(self.test.values)
        self.x_train, self.y_train = self.unique_shapes(self.x_train, self.y_train, self.lag, self.n_features, self.num_of_outputs, self.only_production)
        self.x_test, self.y_test   = self.unique_shapes(self.x_test,  self.y_test,  self.lag, self.n_features, self.num_of_outputs, self.only_production)
        return (self.x_train[:, :, 1:],self.y_train,self.x_test[:, :, 1:],self.y_test)

class SolarDataProcessor:
    def __init__(self, data, n_timesteps, n_outputs, train_start, train_end, test_start, only_production=False):
        self.data = data
        self.n_timesteps = n_timesteps
        self.n_outputs = n_outputs
        self.only_production = only_production
        self.n_features = None

        # DateTimeConverter object
        self.dt_converter = DateTimeConverter(data)
        self.dt_converter.add_month_hour_columns()
        self.dt_converter.add_features()
        #self.dt_converter.remove_features()
        self.data = self.dt_converter.get_data()

        # SplitData object
        self.sd1 = SplitData(
            self.data, n_timesteps, n_outputs, train_start, train_end, test_start, only_production=only_production)
        self.X_train, self.y_train, self.X_test, self.y_test = self.sd1.preprocess_data()

    def get_processed_data(self):
        return self.X_train, self.y_train, self.X_test, self.y_test

