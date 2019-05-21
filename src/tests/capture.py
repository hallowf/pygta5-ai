import time, timeit
import mss
import cv2
import numpy as np
import win32gui, win32ui, win32con, win32api
from statistics import mean

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

if __name__ == '__main__':
    # winapi_test()
    print(timeit.timeit("winapi_timeit_test()", number=3, setup="from __main__ import winapi_timeit_test"))
