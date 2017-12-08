''' Basic Regression Model '''

# Basics
import numpy as np
import pandas as pd
import sklearn as sk
from os.path import dirname
import time
import random
import pickle
# Machine Learning
from sklearn.neural_network import MLPRegressor
from sklearn.linear_model import BayesianRidge, SGDRegressor, LinearRegression
from sklearn import svm
from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor
# Training prep/scoring metrics
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score as r2
# Plotting
import plotly
import plotly.graph_objs as go
from plotly.graph_objs import Scatter, Layout



class ensemble(object):

    def __init__(self, Xtrain, Ytrain, Xtest, Ytest, train_meta, test_meta ):
        # Data
        self.Xtrain = Xtrain
        self.Ytrain = Ytrain
        self.Xtest = Xtest
        self.Ytest = Ytest
        self.train_meta = train_meta
        self.test_meta = test_meta

        # Kfold index generator parameters
        self.__folds = None

        # Initialize regression models
        self._NN_combiner = MLPRegressor()
        self._NN_base = MLPRegressor()
        self._RFR = RandomForestRegressor(max_depth = 4, random_state=0)
        self._BR = BayesianRidge()
        self._ADA = AdaBoostRegressor()
        self._LR = LinearRegression()
        self._SGD = SGDRegressor(max_iter = 1000)

        # Base model info used for training of the combiner model
        self._base_models = [self._RFR, self._BR, self._ADA, self._LR, self._SGD, self._NN_base]
        self.model_columns = ['RFR', 'BR', 'ADA', 'LR', 'SGD', 'base_NN']
        self.reuse_features = ['sub_growth']

        # Initiaize arrays for evaluation metrics
        self.NNinfo = []
        self.NN_baseinfo = []
        self.SVRinfo = []
        self.LRinfo = []
        self.SGDinfo = []
        self.RFRinfo = []
        self.BRinfo = []
        self.ADAinfo = []



    def train(self, cv_folds = 5):

        # Initialize Kfold index generator
        self.__folds = cv_folds
        _kfold = KFold(n_splits = self.__folds, shuffle = True, random_state = 1)


        def _record_info(train_index, test_index, model, name, Xtrain, Ytrain, _iteration):
        # Save model performance metrics from each training iteration

            info_list = []

            # Calculate performance
            train_score = model.score(Xtrain.iloc[train_index,:], Ytrain.iloc[train_index])
            test_score = model.score(Xtrain.iloc[test_index,:], Ytrain.iloc[test_index])

            # Calculate the squared error for training and CV set, save in list
            train_error = (1/len(train_index))*sum((model.predict(Xtrain.iloc[train_index,:]) - Ytrain.iloc[train_index])**2)
            test_error = (1/len(test_index))*sum((model.predict(Xtrain.iloc[test_index,:]) - Ytrain.iloc[test_index])**2)
            info_list.append('**%s**    R2 in I%d: Train: %f, Test: %f' %(name, _iteration, train_score, test_score))
            info_list.append('**%s** Error in I%d: Train: %f, Test: %f' %(name, _iteration, train_error, test_error))

            return info_list



        def _timeit(start_time, model_name):
        # Return the training time of the model given the time at start of training:
            elapsed = time.time() - start_time
            return 'Trained %s in %fs' %(model_name, elapsed)


        def _train_base_models():

            _iteration = 1
            for train_index, test_index in _kfold.split(self.Xtrain):
                print('CV fold: %d' %(_iteration))


                '''Base Neural Network'''
                start = time.time()
                self._NN_base.fit(self.Xtrain.iloc[train_index, :], self.Ytrain[train_index])
                self.NN_baseinfo += _record_info(train_index, test_index, self._NN_base, 'NN_base', self.Xtrain, self.Ytrain, _iteration)
                print(_timeit(start, 'Base_NN'))

                '''Linear Regression'''
                start = time.time()
                self._LR.fit(self.Xtrain.iloc[train_index, :], self.Ytrain[train_index])
                self.LRinfo += _record_info(train_index, test_index, self._LR, 'LR', self.Xtrain, self.Ytrain, _iteration)
                print(_timeit(start, 'Linear Regression'))

                '''Stochastic Gradient Descent'''
                start = time.time()
                self._SGD.fit(self.Xtrain.iloc[train_index, :], self.Ytrain[train_index])
                self.SGDinfo += _record_info(train_index, test_index, self._SGD, 'SGD', self.Xtrain, self.Ytrain, _iteration)
                print(_timeit(start, 'SGD'))

                '''Random Forest Regressor'''
                start = time.time()
                self._RFR.fit(self.Xtrain.iloc[train_index, :], self.Ytrain[train_index])
                self.RFRinfo += _record_info(train_index, test_index, self._RFR, 'RFR', self.Xtrain, self.Ytrain, _iteration)
                print(_timeit(start, 'Random Forest'))

                '''Bayesian Ridge Regression'''
                start = time.time()
                self._BR.fit(self.Xtrain.iloc[train_index, :], self.Ytrain[train_index])
                self.BRinfo += _record_info(train_index, test_index, self._BR, 'BR', self.Xtrain, self.Ytrain, _iteration)
                print(_timeit(start, 'Bayesian Ridge'))

                '''AdaBoost Regressor'''
                start = time.time()
                self._ADA.fit(self.Xtrain.iloc[train_index, :], self.Ytrain[train_index])
                self.ADAinfo += _record_info(train_index, test_index, self._ADA, 'ADA', self.Xtrain, self.Ytrain, _iteration)
                print(_timeit(start, 'AdaBoost'))

                _iteration += 1


        def _train_combiner():
        # Compile Predictions from base models into features for training the Neural Network

            # Restarting Kfold index generator
            _kfold = KFold(n_splits = self.__folds, shuffle = True, random_state = 1)

            # Obtain combiner model features using predictions from base models
            self.NNfeatures = self._ensemble_features(self.Xtrain)

            # Train Neural Network with base model predictions
            _iteration = 1
            for train_index, test_index in _kfold.split(self.NNfeatures):
                print('NN CV fold %d' %(_iteration))

                '''Neural Network Regressor'''
                start = time.time()
                self._NN_combiner.fit(self.NNfeatures.iloc[train_index, :], self.Ytrain[train_index])
                self.NNinfo += _record_info(train_index, test_index, self._NN_combiner, 'NN', self.NNfeatures, self.Ytrain, _iteration)
                _iteration+=1
                print(_timeit(start, 'combiner_NN'))



        _train_base_models()
        _train_combiner()




    def _ensemble_features(self, data):
    # Given a set of base model predictions, return features for the combiner model

        NNfeatures = pd.DataFrame(columns = self.model_columns)
        it = 0
        for model in self._base_models:
            tempPred = model.predict(data)
            NNfeatures[self.model_columns[it]] = tempPred
            it+=1

        tempData = data[self.reuse_features].reset_index(drop = True)
        NNfeatures = pd.concat([NNfeatures, tempData], axis = 1)

        return NNfeatures


    def score(self):
    # Return R2 score of combiner model on test set
        self.NNfeatures = self._ensemble_features(self.Xtest)
        return self._NN_combiner.score(self.NNfeatures, self.Ytest)


    def predict(self, X):
    # Given X, obtain combiner features from base model predictions, then return prediction from combiner
        self.NNfeatures = self._ensemble_features(X)
        return self._NN_combiner.predict(self.NNfeatures)


    def print_training_info(self):
    # Print base model training metrics

        if self.NN_baseinfo:

            # Print metrics for each CV fold
            print('\n**********************')
            print(*self.NN_baseinfo, sep='\n')
            print('\n**********************')
            print(*self.LRinfo, sep='\n')
            print('\n**********************')
            print(*self.SGDinfo, sep='\n')
            print('\n**********************')
            print(*self.RFRinfo, sep='\n')
            print('\n**********************')
            print(*self.BRinfo, sep='\n')
            print('\n**********************')
            print(*self.ADAinfo, sep='\n')
            print('\n**********************')


            # Print score on test set
            print('NN_base test score:  %f' %(self._NN_base.score(self.Xtest, self.Ytest)))
            print('LR test score:       %f' %(self._LR.score(self.Xtest, self.Ytest)))
            print('SGD test score:      %f' %(self._SGD.score(self.Xtest, self.Ytest)))
            print('RFR test score:      %f' %(self._RFR.score(self.Xtest, self.Ytest)))
            print('BR test score:       %f' %(self._BR.score(self.Xtest, self.Ytest)))
            print('ADA test score:      %f' %(self._ADA.score(self.Xtest, self.Ytest)))

        else:
            print('Ensemble must be trained before print_training_info can be called')


    def plot_test_prediction(self, option = 'all', f_name = 'default', auto_open = False, custom_tag = ''):
    # Save plots of combiner model predictions vs. actual

        def plt(ID, symbol, f_name, auto_o, custom_tag):
            X = self.Xtest[self.test_meta.coin_id == ID]
            actual_price = self.Ytest[self.test_meta.coin_id == ID]

            predicted_price = self.predict(X)
            dates = self.test_meta.date[self.test_meta.coin_id == ID]

            Actual = Scatter(
                x = dates,
                y = actual_price,
                name = 'Actual closing Price'
                )

            Prediction = Scatter(
                x = dates,
                y = predicted_price,
                name = 'Predicted closing Price'
                )


            if f_name == 'default':
                fname = '.\model\plots\%s_PredvsActual.html'
            else:
                fname = f_name
            if custom_tag:
                fname = fname[:len(fname)-5] + custom_tag + fname[len(fname)-5:]

            plotData = [Actual, Prediction]
            plotly.offline.plot({'data': plotData,
                                 'layout': {'title': "%s: Normalized Predicted Closing Price vs Actual Closing Price %s" %(symbol, custom_tag)}},
                                  filename = fname %(symbol),
                                  auto_open = auto_o
                                  )

        if option == 'all':
            for ID in pd.unique(self.test_meta.coin_id):
                symbol = self.test_meta.symbol[self.test_meta.coin_id == ID].iloc[0]
                plt(ID, symbol, f_name, auto_open, custom_tag)

        elif option == 'random':
            ID = random.choice(pd.unique(self.test_meta.coin_id))
            symbol = self.test_meta.symbol[self.test_meta.coin_id == ID].iloc[0]
            plt(ID, symbol, f_name, auto_open, custom_tag)

        else:
            ID = option
            symbol = self.test_meta.symbol[self.test_meta.coin_id == ID].iloc[0]
            plt(ID, symbol, f_name, auto_open, custom_tag)

    def save_model(self, path = '.\model\saved_model.sav'):
        pickle.dump(self, open(path, 'wb'))



def load_model(path = '.\model\saved_model.sav'):
    loaded_model = pickle.load(open(path, 'rb'))
    return loaded_model


class features(object):
# Generate clean training and test set for regression model
    def __init__(self, data, split_percent = .8, y_gen = 3):

        self.split_percent = split_percent
        self.y_gen = y_gen

        self.allData = self.__generate_y(data)
        self.split_ind = self.__split()

        self.meta = self.allData.iloc[:, 0:3]
        self.X = self.allData.iloc[:, 3:(self.allData.shape[1]-(self.y_gen+1))]
        self.Y = self.allData.iloc[:, (self.allData.shape[1]-(self.y_gen+1)):]

        if self.Y.shape == (self.Y.shape[0],):
            self.Ytrain = self.Y[:self.split_ind]
            self.Ytest = self.Y[self.split_ind:]
        else:
            self.Ytrain = self.Y.iloc[:self.split_ind, :]
            self.Ytest = self.Y.iloc[self.split_ind:, :]

        self.test_meta = self.meta.iloc[self.split_ind:, :]
        self.train_meta = self.meta.iloc[:self.split_ind, :]
        self.Xtrain = self.X.iloc[:self.split_ind, :]
        self.Xtest = self.X.iloc[self.split_ind:, :]

    def __split(self):
        # Return an index that will ensure that there are no shared cryptocurrencies between test and train set
            ind = int(np.round(len(self.allData))*self.split_percent)
            z = 1
            while self.allData.coin_id[ind] == self.allData.coin_id[ind+z]:
                z+=1
            return ind+z

    def __generate_y(self, data):
    # Generate Y data for n number of days beyond 'current'
        if self.y_gen == 0:
            return data
        else:
            temp = list(data.close)
            size = data.shape[0]
            Y = pd.DataFrame()
            for i in range(self.y_gen + 1):
                if i == 0:
                    Y['today'] = np.ones(size)
                else:
                    Y['%d_day_future' %(i)] = np.ones(size)

            for i in range(self.y_gen + 1):
                Y.iloc[:len(temp)-i, i] = temp[i:len(temp)+1]

            data = pd.concat([data,Y], axis = 1)
            data = data.drop([i for i in range(len(Y)-self.y_gen, len(Y))])
            data = data.drop('close', axis = 1)
        return data
