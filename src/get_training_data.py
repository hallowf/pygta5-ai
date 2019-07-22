import time, os, argparse, sys, socket, pickle
import requests
import numpy as np
import cv2
import mss
import keyboard
import win32api as wapi

from custom_exceptions import UserInterrupt, CrashingRisk

# mss is faster than PIL
# but as fast as win32api
# FPS = 1 / frame loop
sct = mss.mss()


class Watcher(object):
    """Captures images and keypresses and generates training data"""

    def __init__(self, identifier, counter, split_at, delay_save=False, data_limit=50000):
        super(Watcher, self).__init__()
        keyboard.add_hotkey("ctrl+q", self.exit_trigger, args=[])
        keyboard.add_hotkey("t", self.switch_pause, args=[])
        self.paused = False
        u_vals ="\tSplit: %s\n\tResume: %s\n\tDelay save: %s\n\tData limit: %s" % (split_at,
            counter, delay_save, data_limit)
        print("Starting Watcher with ID:%s and Values:\n%s" % (identifier,u_vals))
        print("Press t to pause")
        print("Press ctrl+q to exit")
        self.counter = 0
        self.identifier = identifier
        self.data_limit = data_limit
        self.file_name = "training/training_data_{}.npy".format(self.identifier)
        self.delay_save = delay_save
        self.stop_running = False
        self.do_split = True
        self.split_at = int(split_at)
        self.file_name = "training/training_data_{}{}.npy".format(self.identifier,self.counter)
        self.training_data = None
        self.training_data_lenght = 0
        self.key_list = ["\b", " "]
        for char in "ABCDEFGHIJKLMNOPQRSUVWXYZ123456789":
            self.key_list.append(char)
        self.check_training_data()

    def do_countdown(self):
        for i in list(range(4))[::-1]:
            print(i+1)
            time.sleep(1)


    def exit_trigger(self):
        self.stop_running = True

    def switch_pause(self):
        if self.paused:
            print("Resuming")
        else:
            print("Pausing")
        self.paused = not self.paused

    def __del__(self):
        print("Deleting Watcher")
        if self.delay_save:
            print("Saving on exit")
            # pickle.dump(self.training_data, open(self.file_name, "wb"))
            np.save(self.file_name, self.training_data)

    def split_data(self):
        self.counter += 1
        np.save(self.file_name, self.training_data)
        del self.training_data
        self.training_data = []
        self.training_data_lenght = 0
        self.file_name = "training/training_data_{}{}.npy".format(self.identifier, self.counter)

    def key_check(self):
        keys = []
        for key in self.key_list:
            if wapi.GetAsyncKeyState(ord(key)):
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
                self.training_data_lenght = len(self.training_data)
        else:
            self.training_data = []

    def record(self):
        for i in list(range(4))[::-1]:
            print(i+1)
            time.sleep(1)
        # lst = time.time()
        while(True):
            if not self.paused:
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
                    if self.do_split:
                        if self.training_data_lenght >= self.split_at:
                            print("Splitting data")
                            self.split_data()
                    elif not self.delay_save:
                        print("Saving data")
                        np.save(self.file_name, self.training_data)

    def en_record(self):
        """Experimental recording with the addition of not keeping data,
            and instead sending it to an api"""
        requests.post("http://192.168.1.21:2890/gta-api-watcher-%s?counter=%i&split=%i" % (self.identifier,self.counter,self.split_at))
        self.do_countdown()
        while(True):
            if not self.paused:
                if self.stop_running:
                    self.__del__()
                    raise UserInterrupt("User pressed hotkey")
                output = [0,0,0]
                screen = np.array(sct.grab((0,40,800,640)))
                screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
                screen = cv2.resize(screen, (160,120))
                if keyboard.is_pressed("a") or keyboard.is_pressed("w+a"):
                    output = [1,0,0]
                elif keyboard.is_pressed("d") or keyboard.is_pressed("w+d"):
                    output = [0,0,1]
                elif keyboard.is_pressed("w"):
                    output = [0,1,0]
                else:
                    output = [0,0,0]
                payload = {
                    "screen": screen.tolist(),
                    "output": output
                }
                r = requests.post("http://192.168.1.21:2890/gta-api", json=payload)

    def es_record(self):
        """Experimental socket recording
            Creates a websocket client and sends the data over to a server"""
        HEADERSIZE = 10
        def wait_loop(s):
            msg = s.recv(1024)
            if msg == b"ok":
                return True
            else:
                return False
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("127.0.0.1",2890))
        self.do_countdown()
        username = "%s:%s:%s" % (self.identifier, self.counter, self.split_at)
        id_header = bytes(f'{len(username):<{HEADERSIZE}}', "utf-8")
        id = bytes(username, "utf-8")
        client_socket.send(id_header+id)
        while(True):
            if not self.paused:
                if self.stop_running:
                    self.__del__()
                    raise UserInterrupt("User pressed hotkey")
                output = [0,0,0]
                screen = np.array(sct.grab((0,40,800,640)))
                screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
                screen = cv2.resize(screen, (160,120))
                if keyboard.is_pressed("a") or keyboard.is_pressed("w+a"):
                    output = [1,0,0]
                elif keyboard.is_pressed("d") or keyboard.is_pressed("w+d"):
                    output = [0,0,1]
                elif keyboard.is_pressed("w"):
                    output = [0,1,0]
                else:
                    output = [0,0,0]
                payload = {
                    "screen": screen.tolist(),
                    "output": output
                }
                payload = pickle.dumps(payload)
                payload = bytes(f'{len(payload):<{HEADERSIZE}}', "utf-8") + payload
                # print("len payload",len(payload))
                client_socket.send(payload)
                print("Data sent")
                while not wait_loop(client_socket):
                    print("Waiting for response")
                    time.sleep(0.01)
                print("Response received")



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Capture training data, press ctrl+q to stop recording')
    parser.add_argument("identifier", type=str, help='An identifier for training data file')
    parser.add_argument("--esr", "--exp-socket-record",
        help="Experimental recorder establishes a connection to a socket server", action="store_true")
    # TODO: This argument below should be "machineip:port" and should be checked
    parser.add_argument("--enr", "--exp-net-record",
        help="Experimental recorder that sends data to an api",
        action="store_true")
    parser.add_argument("--s","--split-at", type=int,
        help="An integer to specify when to split data into a new file, and clear memory...")
    parser.add_argument("--r", "--resume-at", type=int,
        help="An integer to specify the counter of the last file training_data_identifier(counter).npy")
    parser.add_argument("--ds", "--delay-save",
        help="Delays saving until Watcher exit",
        action="store_true")
    args = parser.parse_args()
    t = None
    try:
        split_at = getattr(args, "s", None)
        counter = getattr(args, "r", None)
        delay = getattr(args, "ds", False)
        t = Watcher(args.identifier, counter, split_at, delay)
        if args.esr:
            print("Using experimental socket recording")
            t.es_record()
        elif args.enr:
            print("Using experimental network recording")
            t.en_record()
        else:
            t.record()
    except (Exception, UserInterrupt, CrashingRisk) as e:
        en = e.__class__.__name__
        if en == "UserInterrupt" or en == "CrashingRisk" or en == "KeyboardInterrupt":
            del t
            print("Interrupt detected exiting now")
            time.sleep(0.5)
            sys.exit(0)
        else:
            raise e
