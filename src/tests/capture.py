import time, timeit, sys, os
import mss
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
@profile
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


if __name__ == '__main__':
    try:
        capture_memory_test()
        # winapi_test()
        # winapi_Crab_test()
        # mss_test()
        # print(timeit.timeit("winapi_timeit_test()", number=3, setup="from __main__ import winapi_timeit_test"))
    except Exception as e:
        raise e
