# test_model.py

import time, os, argparse
import numpy as np
from keras.models import load_model
import cv2
from alexnet import alexnet
import keyboard
import random
import mss


from custom_exceptions import InvalidBackend, MissingDataSet
from network.tflearn_models import TFModelBuilder

class Player(object):
    """Loads a model and predicts movement,
        requires backend and identifier
        backend(str): keras or tfl
        identifier(str): a string for the data set you created"""

    def __init__(self, backend, identifier, network_type, input_shape=(160,120), *args, **kwargs):
        super(Player, self).__init__()
        self.t_time = 0.09
        backends = ["keras", "tfl"]
        if backend not in backends:
            raise InvalidBackend("Unknown backend %s" % backend)
        width, height = input_shape
        self.network_type = network_type
        self.optzr = kwargs.get("optimizer", None)
        self.lr = kwargs.get("learning_rate", None)
        self.width = width
        self.height = height
        self.input_shape = input_shape
        self.backend = backend
        self.identifier = identifier
        self.model_name = None
        self.model = None
        self.load_trained_model()

    def load_trained_model(self):
        self.load_training_data()
        if backend == "keras":
            self.model = load_model(self.model_name)
        else:
            self.model = TFModelBuilder(self.input_shape, self.network_type, self.lr)
            self.model.load(self.model_name)

    def load_training_data(self):
        if backend == "keras":
            optzr = self.optzr or "Adam"
            self.model_name = "trained_models/%s_%s_%s.h5" % (identifier,
                self.network_type, optzr)
        else:
            lr = self.lr or 1e-3
            self.model_name = "trained_models/%s_%s_%s.h5" % (identifier,
                self.network_type, lr)
        if not os.path.isfile(self.model_name):
            raise MissingDataSet("Couldn't find %s" % self.model_name)

    def straight(self):
    ##    if random.randrange(4) == 2:
    ##        ReleaseKey(W)
    ##    else:
        keyboard.press("w")
        keyboard.release("a")
        keyboard.release("d")

    def left(self):
        keyboard.press("w")
        keyboard.press("a")
        #keyboard.release("w")
        keyboard.release("d")
        #keyboard.release("a")
        time.sleep(0.09)
        keyboard.release("a")

    def right(self):
        keyboard.press("w")
        keyboard.press("d")
        keyboard.release("a")
        #keyboard.release("w")
        #keyboard.release("d")
        time.sleep(0.09)
        keyboard.release("d")

    def play_keras(self):
        sct = mss.mss()
        # last_time = time.time()
        for i in list(range(4))[::-1]:
            print(i+1)
            time.sleep(1)

        paused = False
        while(True):

            if not paused:
                # 800x600 windowed mode
                #screen =  np.array(ImageGrab.grab(bbox=(0,40,800,640)))
                screen = np.array(sct.grab((0,40,800,640)))
                # print('loop took {} seconds'.format(time.time()-last_time))
                last_time = time.time()
                screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
                screen = cv2.resize(screen, (160,120))

                prediction = self.model.predict(screen)[0]
                print(prediction)

                turn_thresh = .75
                fwd_thresh = 0.70

                if prediction[1] > fwd_thresh:
                    straight()
                elif prediction[0] > turn_thresh:
                    left()
                elif prediction[2] > turn_thresh:
                    right()
                else:
                    straight()

            if keyboard.is_pressed("t"):
                paused = True if not paused else False
                time.sleep(5)
                os.system("clear")

    def play_tfl(self):
        sct = mss.mss()
        # last_time = time.time()
        for i in list(range(4))[::-1]:
            print(i+1)
            time.sleep(1)

        paused = False
        while(True):

            if not paused:
                # 800x600 windowed mode
                #screen =  np.array(ImageGrab.grab(bbox=(0,40,800,640)))
                screen = np.array(sct.grab((0,40,800,640)))
                # print('loop took {} seconds'.format(time.time()-last_time))
                last_time = time.time()
                screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
                screen = cv2.resize(screen, (160,120))

                prediction = self.model.predict([screen.reshape(160,120,1)])[0]
                print(prediction)

                turn_thresh = .75
                fwd_thresh = 0.70

                if prediction[1] > fwd_thresh:
                    self.straight()
                elif prediction[0] > turn_thresh:
                    self.left()
                elif prediction[2] > turn_thresh:
                    self.right()
                else:
                    self.straight()

            if keyboard.is_pressed("t"):
                paused = True if not paused else False
                time.sleep(5)
                os.system("clear")

    def run():
        if self.backend == "keras":
            self.play_keras()
        else:
            self.play_tfl()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Trains a model with the data provided")
    parser.add_argument("backend", type=str, help="Backend to use keras or tfl")
    parser.add_argument("identifier", type=str, help="An identifier for training data file")
    parser.add_argument("network", type=str, help="Model to build check instructions.md for available modules")
    parser.add_argument("--optimizer", type=str, help="Optimizer to user with keras models only")
    parser.add_argument("--learning-rate", type=float, help="Learning rate for model currently only used by tflearn")
    args = parser.parse_args()
    try:
        if args.optimizer:
            Player(args.backend,args.identifier, args.network,optimizer=args.optimizer).run()
        elif args.learning_rate:
            Player(args.backend,args.identifier, args.network,learning_rate=args.learning_rate).run()
        else:
            Player(args.backend,args.identifier, args.network).run()
    except (Exception) as e:
        raise e
