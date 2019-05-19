import time
import numpy as np
import cv2
import mss
# mss is faster than PIL
sct = mss.mss()

def process_img(original_image):
    processed_img = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.Canny(processed_img, threshold1=200, threshold2=300)
    return processed_img



lst = time.time()
while(True):
    screen_pil = np.array(sct.grab((0,40,800,640)))
    new_screen = process_img(screen_pil)
    print("Loop took {}".format((time.time()-lst)))
    lst = time.time()
    # cv2.imshow("window", new_screen)
    cv2.imshow("image", screen_pil)
    if cv2.waitKey(25) & 0xFF == ord("q"):
        cv2.destroyAllWindows()
        break
