import os, sys
import keras
from keras.optimizers import Adam, SGD, Adamax, Adadelta, Adagrad, RMSprop, Nadam
from sklearn.model_selection import train_test_split
import numpy as np
import cv2

from network.keras_models import KModelBuilder
from custom_exceptions import InvalidOptimizer, MissingDataSet, InvalidNetworkType


class MainframeKeras(object):
    """Loads the training_data,
        builds a model based on network_type parameter
        also accepts optimizer as parameter
        fits training data into model and saves it"""

    def __init__(self, identifier, network_type="unknown",optimizer="Adam"):
        np.random.seed(3)
        self.identifier = identifier
        self.network_type = network_type
        # BUG: i don't quit remember what this was needed for
        self.classifications = 3
        # create model name and trainind data name
        self.training_data = None
        self.training_data_name = "training/training_data_%s_balanced.npy" % identifier
        self.model_name = "trained_models/%s_%s_%s.h5" % (identifier,self.network_type, optimizer)
        # load the training_data
        self.load_training_data()
        # Map the optimizer and get rid of the others
        self.optzr = self.map_optimizer(optimizer)
        self.optimizer = optimizer

    def load_training_data(self):
        """Loads training data and raises MissingDataSet
            if the file does not exist"""
        if not os.path.isfile(self.training_data_name):
            raise MissingDataSet("Failed to load %s" % self.training_data_name)
        else:
            self.training_data = np.load(self.training_data_name)

    def map_optimizer(self, optimizer):
        # QUESTION: is this even necessary the graphs shows all optimizers,
        # is it due to the imports or the actual existence of them as instantiated objects in memory?
        """Maps an optimizer and gets rid of the others."""
        optimizers = {
            "Adam": Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False),
            "SGD": SGD(lr=0.01, momentum=0.0, decay=0.0, nesterov=False),
            "RMSprop": RMSprop(lr=0.001, rho=0.9, epsilon=None, decay=0.0),
            "Adagrad": Adagrad(lr=0.01, epsilon=None, decay=0.0),
            "Adadelta": Adadelta(lr=1.0, rho=0.95, epsilon=None, decay=0.0),
            "Adamax": Adamax(lr=0.002, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0),
            "Nadam": Nadam(lr=0.002, beta_1=0.9, beta_2=0.999, epsilon=None, schedule_decay=0.004)
        }
        if optimizer not in list(optimizers.keys()):
            raise InvalidOptimizer("%s" % optimizer)
        else:
            optimizer = optimizers[optimizer]
            del optimizers
            return optimizer

    def run(self):
        ## input image dimensions
        img_x, img_y = 160, 120
        input_shape = (img_x, img_y, 1)
        model = KModelBuilder(input_shape,self.network_type).return_model()

        # train and test data
        train = self.training_data[:-500]
        test = self.training_data[-500:]

        # Split data
        X = np.array([i[0] for i in train]).reshape(-1, img_x, img_y, 1)
        Y = [i[1] for i in train]
        test_x = np.array([i[0] for i in test]).reshape(-1, img_x, img_y, 1)
        test_y = [i[1] for i in test]

        # compile the model
        model.compile(loss="categorical_crossentropy", optimizer=self.optzr, metrics=['accuracy'])

        # Create graph dir if necessary
        graph_dir = "./Graph/%s/%s/%s" % (self.identifier,self.network_type,self.optimizer)
        if not os.path.isdir(graph_dir):
            os.makedirs(graph_dir, exist_ok=True)

        # tensorboard data callback
        tbCallBack = keras.callbacks.TensorBoard(log_dir=graph_dir, histogram_freq=0, write_graph=True, write_images=True)

        model.fit(X, Y, batch_size=20, epochs=30, validation_data=(test_x, test_y), callbacks=[tbCallBack])

        if not os.path.isdir("trained_models"):
            os.mkdir("trained_models")
        # Build name: networkType_optimizer__trainingData.h5
        # save weights post training
        model.save(self.model_name)



    # TODO:  maybe split data using train_test_split but this code below is broken
    def old_start(self):
        # split into test and train set
        x_train, x_test, y_train, y_test = train_test_split(self.x, self.y, test_size=.2, random_state=5)



        # convert class vectors to binary class matrices for use in categorical_crossentropy loss below
        # number of action classifications, look for # Bug: in __init__
        y_train = keras.utils.to_categorical(y_train, self.classifications)
        y_test = keras.utils.to_categorical(y_test, self.classifications)

        # Load model and optimizer based on user input
        model = ModelBuilder(input_shape,self.network_type).return_model()

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


        # save weights post training
        model.save(self.model_name)
