import time, os, argparse, sys
# import pickle
import numpy as np
import cv2
import mss
import keyboard
import win32api as wapi

from custom_exceptions import UserInterrupt, CrashingRisk

sct = mss.mss()

class Watcher(object):
    """Captures images and keypresses and generates training data"""

    def __init__(self, identifier, split_at, resume, delay_save=False, data_limit=100000):
        super(Watcher, self).__init__()
        u_vals ="\tSplit: %s\n\tResume: %s\t\nDelay save: %s\t\nData limit: %s" % (split_at,
            resume, delay_save, data_limit)
        print("Starting Watcher with ID:%s and Values:\n" % (identifier,u_vals))
        keyboard.add_hotkey("ctrl+q", self.exit_trigger, args=[])
        print("Press ctrl+q to exit")
        self.train_counter = 0
        self.identifier = identifier
        self.data_limit = data_limit
        self.split_at = None
        self.do_split = False
        self.file_name = "training/training_data_{}.npy".format(self.identifier)
        self.delay_save = delay_save
        self.stop_running = False
        if split_at != None:
            if resume != None:
                self.train_counter = resume
            self.do_split = True
            self.split_at = int(split_at)
            self.file_name = "training/training_data_{}{}.npy".format(self.identifier,self.train_counter)
        self.training_data = None
        self.training_data_lenght = 0
        self.key_list = ["\b", " "]
        for char in "ABCDEFGHIJKLMNOPQRSUVWXYZ123456789":
            self.key_list.append(char)
        self.check_training_data()

    def exit_trigger(self):
        self.stop_running = True

    def __del__(self):
        print("Deleting Watcher")
        if self.delay_save:
            print("Saving on exit")
            # pickle.dump(self.training_data, open(self.file_name, "wb"))
            np.save(self.file_name, self.training_data)

    def split_data(self):
        self.train_counter += 1
        np.save(self.file_name, self.training_data)
        del self.training_data
        self.training_data = []
        self.file_name = "training/training_data_{}{}.npy".format(self.identifier, self.train_counter)

    def key_check(self):
        keys = []
        for key in self.key_list:
            if wapi.GetAsyncKeyState(ord(key)):
                keys.append(key)
        return keys

    def keys_to_output(self,keys):
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
                self.training_data_lenght = len(self.training_data)
        else:
            self.training_data = []

    def record(self):
        for i in list(range(4))[::-1]:
            print(i+1)
            time.sleep(1)
        while(True):
            if self.stop_running:
                self.__del__()
                raise UserInterrupt("User pressed hotkey")
            screen = np.array(sct.grab((0,40,800,640)))
            screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
            screen = cv2.resize(screen, (160,120))
            keys = self.key_check()
            output = self.keys_to_output(keys)
            self.training_data.append([screen, output])
            self.training_data.append([screen, output])
            self.training_data_lenght = len(self.training_data)
            if self.training_data_lenght >= self.data_limit:
                self.__del__()
                raise CrashingRisk("This dataset is now %s of lenght\nClosing program before a crash occurs" % self.training_data_lenght)
            if self.training_data_lenght % 500 == 0:
                print("Current lenght: %s" % self.training_data_lenght)
                if not self.delay_save:
                    print("Saving data")
                    np.save(self.file_name, self.training_data)
                    if self.do_split:
                        if self.training_data_lenght >= self.split_at:
                            print("Splitting data")
                            self.split_data()

    def exp_record(self):
        for i in list(range(4))[::-1]:
            print(i+1)
            time.sleep(1)
        while(True):
            if self.stop_running:
                self.__del__()
                raise UserInterrupt("User pressed hotkey")
            output = [0,0,0]
            screen = np.array(sct.grab((0,40,800,640)))
            screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
            screen = cv2.resize(screen, (160,120))
            if keyboard.is_pressed("a"):
                output = [1,0,0]
            elif keyboard.is_pressed("w"):
                output = [0,1,0]
            elif keyboard.is_pressed("d"):
                output = [0,0,1]
            else:
                output = [0,0,0]
            self.training_data.append([screen, output])
            self.training_data_lenght +=1
            if self.training_data_lenght >= self.data_limit:
                self.__del__()
                raise CrashingRisk("This dataset is now %s of lenght\nClosing program and saving data before a crash occurs" % self.training_data_lenght)
            if self.training_data_lenght % 500 == 0:
                print("Current lenght: %s" % self.training_data_lenght)
                if not self.delay_save:
                    print("Saving data")
                    np.save(self.file_name, self.training_data)
                    if self.do_split:
                        if self.training_data_lenght >= self.split_at:
                            print("Splitting data")
                            self.split_data()




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Capture training data, press ctrl+q to stop recording')
    parser.add_argument("identifier", type=str, help='An identifier for training data file')
    parser.add_argument("--exp-record",
        help="Experimental recorder uses keyboard directly on main loop instead of win32api", action="store_true")
    parser.add_argument("--s","--split-at", type=int,
        help="An integer to specify when to split data into a new file, and clear memory...")
    parser.add_argument("--r", "--resume-at", type=int,
        help="An integer to specify the counter of the last file training_data_identifier(counter).npy")
    parser.add_argument("--ds", "--delay-save",
        help="Delays saving until exit",
        action="store_true")
    args = parser.parse_args()
    t = None
    try:
        split_at = getattr(args, "s", None)
        resume = getattr(args, "r", None)
        delay = getattr(args, "ds", False)
        t = Watcher(args.identifier, split_at, resume, delay)
        if args.exp_record:
            print("Using experimental recording")
            t.exp_record()
        else:
            t.record()
    except (Exception, UserInterrupt, CrashingRisk) as e:
        en = e.__class__.__name__
        if en == "UserInterrupt" or en == "CrashingRisk":
            del t
            print("Interrupt detected exiting now")
            sys.exit(0)
        else:
            raise e
