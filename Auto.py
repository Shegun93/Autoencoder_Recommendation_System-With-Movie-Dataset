# -*- coding: utf-8 -*-
"""

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1P1dn3kHOV3EVN-oIe4Hm7MHicCBaQOhS

import library
"""

import sklearn
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.parallel
import torch.optim as optim
import torch.utils.data
from torch.autograd import Variable

"""Import dataset"""

amazon = pd.read_csv('ratings_Electronics.csv',
                     encoding = 'latin-1', names=['userID','ProductID',
                                           'Ratings','Timestamp'])

recommend = amazon.sample(frac=0.1)

del amazon
#training_set.info()
#amazon['productID'].factorize
recommend['productID'] = pd.factorize(recommend['ProductID'])[0]
recommend['UserID'] = pd.factorize(recommend['userID'])[0]
recommend.drop(['userID', 'ProductID'], axis=1, inplace=True)
columns = ['UserID', 'productID', 'Ratings', 'Timestamp']
recommend.reindex(columns = columns)
new=recommend.head(n=100)

"""Splitting dataset into training_set and test_set"""

from sklearn.model_selection import train_test_split
training_set, test_set = train_test_split(recommend, random_state=42,test_size=0.2)

"""Convert dataset into array"""

#training_set.info()
#training_set['Ratings'].astype(float).astype(int)
training_set = np.array(training_set, dtype = 'int')
test_set = np.array(test_set, dtype = 'int')

"""Get Total Number of users and products"""

nb_users = int(max(max(training_set[:, 3], ), max(test_set[:, 3])))
nb_products = int(max(max(training_set[:, 2], ), max(test_set[:, 2])))

"""Converting the data into an array with users in lines and products in columns"""

def convert(data):
  new_data = []
  for id_users in range(1, nb_users + 1):
    id_products = data[:, 2] [data[:, 3] == id_users]
    id_ratings = data[:, 1] [data[:, 3] == id_users]
    ratings = np.zeros(nb_products)
    ratings[id_products - 1] = id_ratings
    new_data.append(list(ratings))
  return new_data
training_set = convert(training_set)
test_set = convert(test_set)

"""Converting the data into Torch tensors"""

training_set = torch.FloatTensor(training_set)
test_set = torch.FloatTensor(test_set)

"""Creating the architecture of the Neural Network"""

class SAE(nn.Module):
    def __init__(self, ):
        super(SAE, self).__init__()
        self.fc1 = nn.Linear(nb_products, 20)
        self.fc2 = nn.Linear(20, 10)
        self.fc3 = nn.Linear(10, 20)
        self.fc4 = nn.Linear(20, nb_products)
        self.activation = nn.Sigmoid()
    def forward(self, x):
        x = self.activation(self.fc1(x))
        x = self.activation(self.fc2(x))
        x = self.activation(self.fc3(x))
        x = self.fc4(x)
        return x
sae = SAE()
criterion = nn.MSELoss()
optimizer = optim.RMSprop(sae.parameters(), lr = 0.01, weight_decay = 0.5)

"""Training the SAE

Testing the SAE
"""

nb_epoch = 100
for epoch in range(1, nb_epoch + 1):
  train_loss = 0
  s = 0.
  for id_user in range(nb_users):
    input = Variable(training_set[id_user]).unsqueeze(0)
    target = input.clone()
    if torch.sum(target.data > 0) > 0:
      output = sae(input)
      target.require_grad = False
      output[target == 0] = 0
      loss = criterion(output, target)
      mean_corrector = nb_products/float(torch.sum(target.data > 0) + 1e-10)
      loss.backward()
      train_loss += np.sqrt(loss.data*mean_corrector)
      s += 1.
      optimizer.step()
  print('epoch: '+str(epoch)+'loss: '+ str(train_loss/s))

test_loss = 0
s = 0.
for id_user in range(nb_users):
  input = Variable(training_set[id_user]).unsqueeze(0)
  target = Variable(test_set[id_user]).unsqueeze(0)
  if torch.sum(target.data > 0) > 0:
    output = sae(input)
    target.require_grad = False
    output[target == 0] = 0
    loss = criterion(output, target)
    mean_corrector = nb_products/float(torch.sum(target.data > 0) + 1e-10)
    test_loss += np.sqrt(loss.data*mean_corrector)
    s += 1.
print('test loss: '+str(test_loss/s))

