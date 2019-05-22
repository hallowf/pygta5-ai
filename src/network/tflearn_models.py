import tflearn
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
from tflearn.layers.normalization import local_response_normalization


from custom_exceptions import InvalidNetworkType


class TFModelBuilder(object):
    """Builds network models based on input and returns them
        input_shape: tuple(x,y)
        network_type: str(name)
        lr: learning_rate=float"""

    def __init__(self, input_shape=(160,120), network_type="alexnetv2", lr=1e-3):
        super(ModelBuilder, self).__init__()
        self.network_type = network_type
        width, height = input_shape
        self.width = width
        self.height = height
        self.lr = lr
        self.models = {
            "alexnetv2": self.build_alexnetv2
        }
        if network_type not in list(self.models.keys()):
            raise InvalidNetworkType("Unknown network_type: %s" % network_type)

    def return_model(self):
        return self.models[self.network_type](self.width,self.height, self.lr)


    def build_alexnetv2(self,width, height, lr):
        """ AlexNet.
        References:
            - Alex Krizhevsky, Ilya Sutskever & Geoffrey E. Hinton. ImageNet
            Classification with Deep Convolutional Neural Networks. NIPS, 2012.
        Links:
            - [AlexNet Paper](http://papers.nips.cc/paper/4824-imagenet-classification-with-deep-convolutional-neural-networks.pdf)
        """
        network = input_data(shape=[None, width, height, 1], name='input')
        network = conv_2d(network, 96, 11, strides=4, activation='relu')
        network = max_pool_2d(network, 3, strides=2)
        network = local_response_normalization(network)
        network = conv_2d(network, 256, 5, activation='relu')
        network = max_pool_2d(network, 3, strides=2)
        network = local_response_normalization(network)
        network = conv_2d(network, 384, 3, activation='relu')
        network = conv_2d(network, 384, 3, activation='relu')
        network = conv_2d(network, 256, 3, activation='relu')
        network = max_pool_2d(network, 3, strides=2)
        network = local_response_normalization(network)
        network = fully_connected(network, 4096, activation='tanh')
        network = dropout(network, 0.5)
        network = fully_connected(network, 4096, activation='tanh')
        network = dropout(network, 0.5)
        network = fully_connected(network, 3, activation='softmax')
        network = regression(network, optimizer='momentum',
                             loss='categorical_crossentropy',
                             learning_rate=lr, name='targets')

        model = tflearn.DNN(network, checkpoint_path='model_alexnet',
                            max_checkpoints=1, tensorboard_verbose=2, tensorboard_dir='Graph')

        return model
