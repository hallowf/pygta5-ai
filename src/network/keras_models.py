from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D

from custom_exceptions import InvalidNetworkType

class KModelBuilder(object):
    """Builds network models based on input and returns them"""

    def __init__(self, input_shape, network_type="unknown", classifications=3):
        super(KModelBuilder, self).__init__()
        self.classifications = classifications
        self.network_type = network_type
        self.input_shape = input_shape
        self.models = {
            "unknown": self.build_unknown_model,
            "CIFAR10": self.build_CIFAR10,
            "MLP": self.build_MLP_unknown,
            "VGG": self.build_VGG
        }
        if network_type not in list(self.models.keys()):
            raise InvalidNetworkType("Unknown network_type: %s" % network_type)

    def return_model(self):
        model = self.models[self.network_type](self.input_shape)
        print(model.summary())
        return model

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
