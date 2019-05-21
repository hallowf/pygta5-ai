import time, os
import numpy as np
import cv2
import mss
from getKeys import key_check, keyboard_check

# mss is faster than PIL
# but as fast as win32api
# FPS = 1 / frame loop
sct = mss.mss()

def keys_to_output(keys):
    # [A,W,D]
    output = [0,0,0]

    if "A" in keys:
        output[0] = 1
    elif "W" in keys:
        output[1] = 1
    else:
        output[2] = 1

    return output


def main():
    file_name = "training_data.npy"
    for i in list(range(4))[::-1]:
        print(i+1)
        time.sleep(1)

    lst = time.time()
    while(True):
        screen = np.array(sct.grab((0,40,800,640)))
        print("Loop took {}".format((time.time()-lst)))
        lst = time.time()
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

if __name__ == '__main__':
    main()
