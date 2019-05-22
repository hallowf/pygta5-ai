import numpy as np
from network.alexnet import alexnet
import keras

from network.tflearn_models import TFModelBuilder

class MainframeTFLearn(object):
    # QUESTION: alexnet or tflearn seems to have no need for compilation
    # just create the model split the data and fit, no optimizer?,
    # n_epoch instead of epochs? snapshot_step?
    """Same as MainframeKeras but for tflearn"""

    def __init__(self, identifier, network_type="alexnetv2", lr=1e-3):
        self.identifier = identifier
        self.network_type = network_type
        self.training_data = None
        self.lr = lr
        # create model name and training data name
        self.training_data_name = "training/training_data_%s_balanced.npy" % identifier
        self.model_name = "trained_models/%s_%s_%s.h5" % (self.network_type, self.optimizer, identifier)
        # load the training_data
        self.load_training_data = load_training_data()

    def load_training_data(self):
        """Loads training data and raises MissingDataSet
            if the file does not exist"""
        if not os.path.isfile(self.training_data_name):
            raise MissingDataSet("Failed to load %s" % self.training_data_name)
        else:
            self.training_data = np.load(self.training_data_name)

    def start(self):
        ## input image dimensions
        img_x, img_y = 160, 120
        input_shape = (img_x,img_y)
        model = TFModelBuilder(input_shape,self.network_type, self.lr)

        # train and test data
        train = self.training_data[:-500]
        test = self.training_data[-500:]

        # Split data
        X = np.array([i[0] for i in train]).reshape(-1, img_x, img_y, 1)
        Y = [i[1] for i in train]
        test_x = np.array([i[0] for i in test]).reshape(-1, img_x, img_y, 1)
        test_y = [i[1] for i in test]

        # Create graph dir if necessary
        graph_dir = "./Graph/%s/%s" % (self.identifier,self.network_type)
        if not os.path.isdir(graph_dir):
            os.makedirs(graph_dir, exist_ok=True)

        # tensorboard data callback <- will this work with tflearn
        tbCallBack = keras.callbacks.TensorBoard(log_dir=graph_dir, histogram_freq=0, write_graph=True, write_images=True)

        model.fit({'input': X}, {'targets': Y}, n_epoch=60, validation_set=({'input': test_x}, {'targets': test_y}),
                    snapshot_step=500, show_metric=True, callbacks=[tbCallBack])
        # keras like
        # model.fit(X, Y, batch_size=20, epochs=30, validation_data=(test_x, test_y), callbacks=[tbCallBack])

        if not os.path.isdir("trained_models"):
            os.mkdir("trained_models")
        # Build name: networkType_optimizer__trainingData.h5
        # save weights post training
        model.save(self.model_name)
