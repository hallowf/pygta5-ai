import time, os, argparse, sys
import numpy as np
import cv2
import mss
import keyboard
import win32api as wapi

from custom_exceptions import UserInterrupt

# mss is faster than PIL
# but as fast as win32api
# FPS = 1 / frame loop
sct = mss.mss()


class Trainer(object):
    """docstring for Trainer."""

    def __init__(self, identifier):
        super(Trainer, self).__init__()
        self.train_counter = 0
        self.identifier = identifier
        self.file_name = "training/training_data_{}.npy".format(self.identifier)
        self.training_data = None
        self.keyList = ["\b", " "]
        self.key_list = ["space"]
        for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789":
            self.keyList.append(char)
            self.key_list.append(char.lower())
        self.check_training_data()

    def key_check(self):
        keys = []
        for key in self.keyList:
            if wapi.GetAsyncKeyState(ord(key)):
                keys.append(key)
        return keys

    def keyboard_check(self):
        keys = []
        for key in self.key_list:
            if keyboard.is_pressed(key):
                keys.append(key)
        return keys

    def keys_to_output(self,keys):
        # [A,W,D]
        output = [0,0,0]

        if "A" in keys:
            output[0] = 1
        elif "W" in keys:
            output[1] = 1
        else:
            output[2] = 1

        return output

    def check_training_data(self):
        if not os.path.isdir("training"):
            os.mkdir("training")
        if os.path.isfile(self.file_name):
                self.training_data = list(np.load(self.file_name))
        else:
            self.training_data = []

    def record(self):
        for i in list(range(4))[::-1]:
            print(i+1)
            time.sleep(1)
        lst = time.time()
        while(True):
            if keyboard.is_pressed("t"):
                raise UserInterrupt("Stoping recorder")
            screen = np.array(sct.grab((0,40,800,640)))
            screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
            screen = cv2.resize(screen, (160,120))
            keys = self.key_check()
            output = self.keys_to_output(keys)
            self.training_data.append([screen, output])
            print("Loop took {}".format((time.time()-lst)))
            lst = time.time()
            if len(self.training_data) % 500 == 0:
                print("Saving data")
                np.save(self.file_name, self.training_data)

    def exp_record(self):
        for i in list(range(4))[::-1]:
            print(i+1)
            time.sleep(1)
        lst = time.time()
        while(True):
            if keyboard.is_pressed("t"):
                raise UserInterrupt("Stoping recorder")
            output = None
            screen = np.array(sct.grab((0,40,800,640)))
            screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
            screen = cv2.resize(screen, (160,120))
            if keyboard.is_pressed("a"):
                output = [1,0,0]
            elif keyboard.is_pressed("w"):
                output = [0,1,0]
            else:
                output = [0,0,1]
            self.training_data.append([screen, output])
            print("Loop took {}".format((time.time()-lst)))
            lst = time.time()
            if len(self.training_data) % 500 == 0:
                print("Saving data")
                np.save(self.file_name, self.training_data)




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Capture training data')
    parser.add_argument("identifier", type=str, help='An identifier for training data file')
    parser.add_argument("--exp-record",
        help="Experimental recorder uses keyboard directly on main loop instead of win32api", action="store_true")
    args = parser.parse_args()
    try:
        t = Trainer(args.identifier)
        if args.exp_record:
            t.exp_record()
        else:
            t.record()
    except (Exception, UserInterrupt) as e:
        ex_name = e.__class__.__name__
        if ex_name == "UserInterrupt":
            print("Interrupt detected exiting now")
            sys.exit(0)
        else:
            raise e
