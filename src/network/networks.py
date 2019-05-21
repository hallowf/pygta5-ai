import os, sys, time, threading
import keyboard
import keras
from keras.models import load_model
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras.optimizers import Adam, SGD, Adamax, Adadelta, Adagrad, RMSprop, Nadam
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn import preprocessing
import cv2

from custom_exceptions import InvalidOptimizer, MissingDataSet


class CNN(object):
    """Loads the training_data,
    builds a model based on network_type parameter
    also accepts optimizer as parameter
    fits training data into model and saves it"""

    def __init__(self, identifier, network_type="unknown",optimizer="Adam"):
        np.random.seed(3)
        self.models = {
            "unknown": self.build_unknown_model,
            "CIFAR10": self.build_CIFAR10,
            "MLP": self.build_MLP_unknown,
            "VGG": self.build_VGG
        }
        if network_type not in list(self.models.keys()):
            sys.stdout.write("Invalid network type: %s\n" % network_type)
        self.identifier = identifier
        self.optzr = self.map_optimizer(optimizer)
        self.network_type = network_type
        self.classifications = 3
        self.training_data = None
        self.training_data_name = "training/training_data_%s_balanced.npy" % identifier
        # map trained data

    def load_training_data(self):
        if not os.path.isfile(self.training_data_name):
            raise MissingDataSet("Failed to load %s" % self.training_data_name)
        else:
            self.training_data = np.load(self.training_data_name)

    def map_optimizer(self, optimizer):
        optimizers = {
            "Adam": Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False),
            "SGD": SGD(lr=0.01, momentum=0.0, decay=0.0, nesterov=False),
            "RMSprop": RMSprop(lr=0.001, rho=0.9, epsilon=None, decay=0.0),
            "Adagrad": Adagrad(lr=0.01, epsilon=None, decay=0.0),
            "Adadelta": Adadelta(lr=1.0, rho=0.95, epsilon=None, decay=0.0),
            "Adamax": Adamax(lr=0.002, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0),
            "Nadam": Nadam(lr=0.002, beta_1=0.9, beta_2=0.999, epsilon=None, schedule_decay=0.004)
        }
        if optimizer not in list(self.optimizers.keys()):
            sys.stdout.write("Invalid optimizer: %s\n" % optimizer)
            raise InvalidOptimizer("%s" % optimizer)
        else:
            return optimizers[optimizer]

    def build_VGG(self, input_shape):
        model = Sequential()
        # input: input_shape images with 3 channels -> (x?, y?, z?) tensors.
        # this applies 32 convolution filters of size 3x3 each.
        model.add(Conv2D(32, (2, 2), activation='relu', input_shape=input_shape))
        model.add(Conv2D(32, (2, 2), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))

        model.add(Conv2D(64, (2, 2), activation='relu'))
        model.add(Conv2D(64, (2, 2), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))

        model.add(Flatten())
        model.add(Dense(256, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(self.classifications, activation='softmax'))
        return model

    def build_MLP_unknown(self, input_shape):
        model = Sequential()
        model.add(Conv2D(100, kernel_size=(2, 2), strides=(2, 2), activation='relu', input_shape=input_shape))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Flatten())
        model.add(Dense(64, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(64, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(self.classifications, activation='sigmoid'))
        return model

    # simple deep CNN
    def build_CIFAR10(self, input_shape):
        model = Sequential()
        model.add(Conv2D(32, (2, 2), padding='same',
                         input_shape=input_shape))
        model.add(Activation('relu'))
        model.add(Conv2D(32, (2, 2)))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))

        model.add(Conv2D(64, (2, 2), padding='same'))
        model.add(Activation('relu'))
        model.add(Conv2D(64, (2, 2)))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))

        model.add(Flatten())
        model.add(Dense(512))
        model.add(Activation('relu'))
        model.add(Dropout(0.5))
        model.add(Dense(self.classifications))
        model.add(Activation('softmax'))
        return model

    def build_unknown_model(self,input_shape):
        # CNN model
        model = Sequential()
        model.add(Conv2D(100, kernel_size=(2, 2), strides=(2, 2), activation='relu', input_shape=input_shape))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Flatten())
        model.add(Dense(250, activation='relu'))
        model.add(Dense(self.classifications, activation='softmax'))
        return model



    def start(self):
        # split into test and train set
        x_train, x_test, y_train, y_test = train_test_split(self.x, self.y, test_size=.2, random_state=5)

        ## input image dimensions
        img_x, img_y = 160, 120
        input_shape = (img_x, img_y, 1)

        # convert class vectors to binary class matrices for use in categorical_crossentropy loss below
        # number of action classifications
        y_train = keras.utils.to_categorical(y_train, self.classifications)
        y_test = keras.utils.to_categorical(y_test, self.classifications)

        # Load model and optimizer based on user input
        model = self.models[self.network_type](input_shape)

        model.compile(loss="categorical_crossentropy", optimizer=self.optzr, metrics=['accuracy'])

        graph_dir = "./Graph/%s/%s" % (self.network_type,self.optimizer)
        if not os.path.isdir(graph_dir):
            os.makedirs(graph_dir, exist_ok=True)
        # tensorboard data callback
        tbCallBack = keras.callbacks.TensorBoard(log_dir=graph_dir, histogram_freq=0, write_graph=True, write_images=True)

        model.fit(x_train, y_train, batch_size=20, epochs=30, validation_data=(x_test, y_test), callbacks=[tbCallBack])
        if not os.path.isdir("trained_models"):
            os.mkdir("trained_models")
        # Build name: networkType_optimizer_set(X)_trainingData.h5
        model_name = "trained_models/%s_%s_set%s.h5" % (self.network_type, self.optimizer, self.set)

        # save weights post training
        model.save(model_name)
