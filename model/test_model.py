# Basics
import pandas as pd
import numpy as np

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

# Plot Results:
ensemble.plot_test_prediction()
