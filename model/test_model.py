# Basics
import pandas as pd
import numpy as np
import pickle

# Custom
from model import model
import time
from importlib import reload


# Import cleaned data
data = pd.read_csv('./model/data/training_data.csv', index_col = 0)
data = data.reset_index(drop = True)
data = data.iloc[:7000,:]

# Create features for model
features = model.features(data)
Xtrain = features.Xtrain
Xtest = features.Xtest
Ytrain = features.Ytrain.iloc[:,2]
Ytest = features.Ytest.iloc[:,2]
test_meta = features.test_meta
train_meta = features.train_meta

# Train model, display test metrics
ensemble = model.ensemble(Xtrain, Ytrain, Xtest, Ytest, train_meta, test_meta)
ensemble.train()
print('Combiner score: %f' %(ensemble.score()))


'''
Default save/load path is '.\model\saved_model.sav', but you can save/load to a custom path
with ensemble.save_model(path) and model.load_model(path)
'''

# Save model:
ensemble.save_model()

# Load model and test
unpickled_ensemble = model.load_model()
print('Score from unpickled model: ' %(unpickled_ensemble.score()))
unpickled_predictions = unpickled_ensemble.predict(Xtest)



# Plot Results:
# ensemble.plot_test_prediction()
