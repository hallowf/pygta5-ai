import time, timeit, sys, os, json, socket, pickle, random
import mss
import requests
import keyboard
import cv2
import numpy as np
import win32gui, win32ui, win32con, win32api
from statistics import mean

# from memory_profiler import profile
from utils import UserInterrupt, h_profile

class CrabScreen(object):
    """preserving the handles?"""

    def __init__(self, region=(0,40,800,640)):
        super(CrabScreen, self).__init__()
        self.region = region
        left,top,x2,y2 = region
        self.left = left
        self.top = top
        self.width = x2 - left + 1
        self.height = y2 - top + 1
        self.hwin = win32gui.GetDesktopWindow()
        self.hwindc = win32gui.GetWindowDC(self.hwin)
        self.srcdc = win32ui.CreateDCFromHandle(self.hwindc)
        self.memdc = self.srcdc.CreateCompatibleDC()
        self.bmp = None

    def __del__(self):
        self.srcdc.DeleteDC()
        self.memdc.DeleteDC()
        win32gui.ReleaseDC(self.hwin, self.hwindc)
        if self.bmp != None:
            try:
                win32gui.DeleteObject(self.bmp.GetHandle())
            except Exception as e:
                raise e

    def snap(self):
        self.bmp = win32ui.CreateBitmap()
        self.bmp.CreateCompatibleBitmap(self.srcdc, self.width, self.height)
        self.memdc.SelectObject(self.bmp)
        self.memdc.BitBlt((0, 0), (self.width, self.height), self.srcdc, (self.left, self.top), win32con.SRCCOPY)

        signedIntsArray = self.bmp.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
        img.shape = (self.height,self.width,4)
        win32gui.DeleteObject(self.bmp.GetHandle())
        self.bmp = None
        return img

def grab_screen(region=(0,40,800,640)):

    hwin = win32gui.GetDesktopWindow()

    left,top,x2,y2 = region
    width = x2 - left + 1
    height = y2 - top + 1

    hwindc = win32gui.GetWindowDC(hwin)
    srcdc = win32ui.CreateDCFromHandle(hwindc)
    memdc = srcdc.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(srcdc, width, height)
    memdc.SelectObject(bmp)
    memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)

    signedIntsArray = bmp.GetBitmapBits(True)
    img = np.fromstring(signedIntsArray, dtype='uint8')
    img.shape = (height,width,4)

    srcdc.DeleteDC()
    memdc.DeleteDC()
    win32gui.ReleaseDC(hwin, hwindc)
    win32gui.DeleteObject(bmp.GetHandle())

    return img

def winapi_Crab_test():
    sct = CrabScreen()
    for i in list(range(4))[::-1]:
        print(i+1)
        time.sleep(1)

    lst = time.time()
    for i in list(range(200))[::-1]:
        screen_pil = np.array(sct.snap())
        tm = time.time()-lst
        print("Loop took {}".format(tm))
        # vals.append(tm)
        lst = time.time()
        cv2.imshow("image", screen_pil)
        if cv2.waitKey(25) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            break
    cv2.destroyAllWindows()

def winapi_test():
    # vals = []
    for i in list(range(4))[::-1]:
        print(i+1)
        time.sleep(1)

    lst = time.time()
    for i in list(range(200))[::-1]:
        screen_pil = np.array(grab_screen())
        tm = time.time()-lst
        print("Loop took {}".format(tm))
        # vals.append(tm)
        lst = time.time()
        cv2.imshow("image", screen_pil)
        if cv2.waitKey(25) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            break
    cv2.destroyAllWindows()
    # print(mean(vals))

def winapi_timeit_test():
    print("winapi timeit test")
    for i in list(range(200))[::-1]:
        screen_pil = np.array(grab_screen())

def mss_timeit_test():
    print("mss timeit test")
    sct = mss.mss()
    for i in list(range(200))[::-1]:
        screen_pil = np.array(sct.grab((0,40,800,640)))

def mss_test():
    # vals = []
    sct = mss.mss()
    for i in list(range(4))[::-1]:
        print(i+1)
        time.sleep(1)

    lst = time.time()
    for i in list(range(200))[::-1]:
        screen_pil = np.array(sct.grab((0,40,800,640)))
        tm = (time.time()-lst)
        print("Loop took {}".format(tm))
        # vals.append(tm)
        lst = time.time()
        cv2.imshow("image", screen_pil)
        if cv2.waitKey(25) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            break
    cv2.destroyAllWindows()
    # print(mean(vals))

# @h_profile
# @profile
def capture_memory_test():
    print("Starting")
    sct = mss.mss()
    training_data = []
    file_name = "test_capture.npy"
    for i in list(range(5000))[::-1]:
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
        training_data.append([screen, output])
        if len(training_data) % 1000 == 0:
            print("Saving data")
            np.save(file_name, training_data)

def api_send_test():
    sct = mss.mss()
    for i in list(range(5000))[::-1]:
        lst = time.perf_counter()
        print("last",lst)
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
        payload = {
            "screen": screen.tolist(),
            "output": output,
            "time": lst
        }
        r = requests.post("http://127.0.0.1:2890/gta-api", json=payload)
        print(r.text)

def websocket_server_test():
    def wait_loop(cs):
        msg = cs.recv(1024)
        if msg == b"ok":
            return True
        else:
            return False
    sct = mss.mss()
    HEADERSIZE = 10
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 2890))
        s.listen(5)
        while True:
            cs, addr = s.accept()
            for i in list(range(700))[::-1]:
                lst = time.time()
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
                payload = {
                    "screen": screen.tolist(),
                    "output": output,
                    "time": lst
                }
                payload = pickle.dumps(payload)
                payload = bytes(f'{len(payload):<{HEADERSIZE}}', "utf-8") + payload
                cs.send(payload)
                print("Data sent")
                while not wait_loop(cs):
                    print("Waiting for response")
                    time.sleep(0.1)
                print("Response received")
                print("TIME:", time.time()-lst)
            break




def websocket_client_test():
    names = ["test%s" % i for i in range(25)]
    user_id = random.choice(names)
    time_mean = 0
    lowest = 0.9
    highest = 0.01
    time_list = []
    def wait_loop(s):
        msg = s.recv(1024)
        if msg == b"ok":
            return True
        else:
            return False
    sct = mss.mss()
    HEADERSIZE = 10
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("127.0.0.1",2890))
    # receive functionality won't be blocking
    # client_socket.setblocking(False)
    id_header = bytes(f'{len(user_id):<{HEADERSIZE}}', "utf-8")
    id = bytes(user_id, "utf-8")
    client_socket.send(id_header+id)
    print("Starting in 3 seconds")
    time.sleep(3)
    while True:
        for i in list(range(2000))[::-1]:
            lst = time.time()
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
            lst = time.time()-lst
            time_list.append(lst)
            if lst < lowest:
                lowest = lst
            if lst > highest:
                highest = lst
            print("TIME:", lst)
        break
    # check mean
    time_mean = float(mean(time_list))
    values = "\nHigh: %f\nLow: %f\nMean: %f" % (highest, lowest, time_mean)
    print(values)

if __name__ == '__main__':
    try:
        # NOTE: sockets seems to be really fast
        websocket_client_test()
        # websocket_server_test()
        # api_send_test()
        # winapi_test()
        # winapi_Crab_test()
        # mss_test()
        # print(timeit.timeit("winapi_timeit_test()", number=3, setup="from __main__ import winapi_timeit_test"))
    except Exception as e:
        raise e
