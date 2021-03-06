#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  9 14:18:53 2017

@author: KarimM
"""

import numpy as np 
from random import gauss
import sys
from math import exp
import pickle
from numpy import genfromtxt

""" 
Activation Functions
"""
# ReLu Activation Function
def relu(input):
    return np.maximum(input, 0.0)

# ReLu derivative [[[Make it applicable on vectors]]]
def relu_diff(input):
    if input > 0: 
        return 1.0 
    else: 
        return 0.001

def sigmoid(activation):
    if activation < 0.0:
        return 1.0 - 1.0 / (1.0 + exp(activation))
    return 1.0 / (1.0 + exp(-activation))
        
def sigmoid_diff(output):
	return output * (1.0 - output)

def softmax(x):
    """Compute the softmax of vector x in a numerically stable way."""
    shiftx = x - np.max(x)
    exps = np.exp(shiftx)
    return exps / np.sum(exps)

"""
Network Implementation
"""
# Initializing the network
def initialize_network(*args):
    network = list()
    for layer_number in range(1,len(args)):
        layer = [{'weights':[abs(gauss(0,0.001)) for i in range(args[layer_number-1] + 1)],
                             'updatedWeights':[0.0] * (args[layer_number-1] + 1),
                             'output':0.0,
                             'delta':0.0,
                             } for i in range(args[layer_number])]
        network.append(layer)
    return network

#Calculate neuron activation for an input
def MultiplyWeight(weights, inputs):
    activation = np.dot(weights[:-1],inputs)
    activation += weights[-1]
    return activation

# Forward propagate input to a network output [[[Get rid of loops]]]
def forward_propagate(network, row):
    inputs = row
    for i in range(len(network)):
        layer = network[i]
        new_inputs = []
        for neuron in layer:
            z = MultiplyWeight(neuron['weights'], inputs)
            if (i == (len(network) - 1)):
                neuron['output'] = z
                neuron['output'] = sigmoid(z)
            else:
                neuron['output'] = relu(z)
            new_inputs.append(neuron['output'])
        inputs = new_inputs
    #inputs = softmax(inputs)
#    for i in range(len(network[-1])-1):
#        network[-1][i]['output'] = inputs[i]
    return inputs

# Backpropagate error and store in neurons  [[[Get rid of loops]]]
def backward_propagate_error(network, expected,row,l_rate):
    for i in reversed(range(len(network))):
        layer = network[i]
        errors = list()
        if i != len(network)-1:
            for j in range(len(layer)):
                error = 0.0
                for neuron in network[i + 1]:
                    error += (neuron['weights'][j] * neuron['delta'])
                errors.append(error)
        else:
            for j in range(len(layer)):
                neuron = layer[j]
                errors.append(expected[j] - neuron['output']) # For squared error -> change to entropy
        for j in range(len(layer)):
            neuron = layer[j]
            if (i == len(network)-1):
                neuron['delta'] = errors[j] * sigmoid_diff(neuron['output'])
            else: 
                neuron['delta'] = errors[j] * relu_diff(neuron['output'])              
    # updating the weights for using mini batch gradient decent
    for i in range(len(network)):
        inputs = row[:-1]
        if i != 0:
            inputs = [neuron['output'] for neuron in network[i - 1]]
        for neuron in network[i]:
            for j in range(len(inputs)):
                neuron['updatedWeights'][j] += neuron['delta'] * inputs[j]
            neuron['updatedWeights'][-1] += neuron['delta']
            
            
# Update network weights with error  [[[Get rid of loops]]]
def update_weights(network,l_rate):
    for layer in network:
        for neuron in layer:
            for j in range(len(neuron['weights'])):
                neuron['weights'][j] += l_rate * neuron['updatedWeights'][j]
                neuron['updatedWeights'][j] = 0
            
            
# Train a network for a fixed number of epochs
def train_network(network, train, l_rate, n_epoch, n_outputs,batchSize):
    errors = list()
    for epoch in range(n_epoch):
        sum_error = 0.0
        for i in range(len(train)):
            #print i 
            row = train[i]
            outputs = forward_propagate(network, row[:-1])
            expected = [0 for k in range(n_outputs)]
            expected[row[-1]] = 1
            sum_error += sum([(expected[j]-outputs[j])**2 for j in range(len(expected))])
            #sum_error += sum([(expected[j]* np.log(outputs[j])) for j in range(len(expected))])
            backward_propagate_error(network, expected, row, l_rate)
            if (i % batchSize == 0):
                update_weights(network,l_rate)
        errors.append(sum_error)
        if (epoch % 5 == 0):
            print('>epoch=%d, lrate=%.3f, error=%.3f' % (epoch, l_rate, sum_error))
    with open("error.txt", 'a') as file_handler:
        for item in errors:
            file_handler.write("{0}\n".format(item))
        
# Make a prediction with a network
def predict(network, row):
    outputs = forward_propagate(network, row)
    return outputs.index(max(outputs))

"""
Evaluation Section
"""
# Calculate accuracy percentage
def accuracy_metric(actual, predicted):
	correct = 0
	for i in range(len(actual)):
		if actual[i] == predicted[i]:
			correct += 1
	return correct / float(len(actual)) * 100.0

def testingNetwork(dataSet,network):
    predictions = []
    for i in range(len(dataSet)):
        predictions.append(predict(network,dataSet[i][:-1]))
    actual = [row[-1] for row in dataSet]
    return accuracy_metric(actual,predictions)


"""
Saving and Loading the net
"""
def saveNet(net,fileName):
    with open(fileName, "wb") as fp:   #Pickling
        pickle.dump(net, fp)

def loadNet(fileName):
    with open(fileName, "rb") as fp:   # Unpickling
        net = pickle.load(fp)
    return net


"""
x_training = genfromtxt('../../data/Question2_123/x_train.csv',delimiter = ",")
y_training = genfromtxt('../../data/Question2_123/y_train.csv',delimiter = ",")
x_training = x_training.astype(int)
y_training = y_training.astype(int)
y_training = y_training.reshape([len(y_training),1])
TrainData = np.append(x_training, y_training, axis=1)  
#net = initialize_network(14,100,40,4)
net = loadNet("network.txt")
train_network(net,TrainData[1:1000],0.05,100,4,10)
saveNet(net,"network.txt")
"""

"""
import matplotlib.pyplot as plt
err = list() 
with open("/Users/KarimM/Desktop/CloudOutputs/error.txt", 'r') as file_handler:
        for line in file_handler:
            err.append(float(line))
plt.plot(err)
"""


"""
x_training = genfromtxt("/Users/KarimM/Google Drive/PhD/Courses/Deep Learning/assignment1/Question2_123/x_train.csv",delimiter = ",")
y_training = genfromtxt("/Users/KarimM/Google Drive/PhD/Courses/Deep Learning/assignment1/Question2_123/y_train.csv",delimiter = ",")
x_training = x_training.astype(int)
y_training = y_training.astype(int)
y_training = y_training.reshape([len(y_training),1])
TrainData = np.append(x_training, y_training, axis=1)      
"""

"""
x_training = genfromtxt("../../assignment1/Question2_123/x_train.csv",delimiter = ",")
y_training = genfromtxt("../../assignment1/Question2_123/y_train.csv",delimiter = ",")
x_training = x_training.astype(int)
y_training = y_training.astype(int)
y_training = y_training.reshape([len(y_training),1])
TrainData = np.append(x_training, y_training, axis=1)
"""

"""
net = initialize_network(14,4,4)
net = initialize_network(14,28,28,28,28,28,28,4)
train_network(net,TrainData[0:1000],0.03,100,4,100)
"""