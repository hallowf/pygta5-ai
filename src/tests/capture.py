import time
import mss
import cv2
import numpy as np
import win32gui, win32ui, win32con, win32api
from statistics import mean

def grab_screen(region=(0,40,800,640)):

    hwin = win32gui.GetDesktopWindow()

    if region:
            left,top,x2,y2 = region
            width = x2 - left + 1
            height = y2 - top + 1
    else:
        width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

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

    return cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

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


def mss_test():
    vals = []
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
    # mss ~~0.06409240908183335
    # winapi ~~0.06700372695922852
    # mss with mean 0.06502873063087464
    # winapi with mean 0.07244414329528809
    winapi_test()
