import time
import numpy as np
import cv2
import mss
# mss is faster than PIL
sct = mss.mss()


def roi(img, verts):
    # create mask based on image
    mask = np.zeros_like(img)
    # fill mask
    cv2.fillPoly(mask, verts, 255)
    # apply mask over image only roi remains
    masked = cv2.bitwise_and(img,mask)
    return masked

def draw_lines(img,lines):
    try:
        for line in lines:
            coords = line[0]
            cv2.line(img, (coords[0],coords[1]), (coords[2],coords[3]), [255,255,255], 3)
    except:
        pass


def process_img(original_image):
    processed_img = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.Canny(processed_img, threshold1=200, threshold2=300)
    processed_img = cv2.GaussianBlur(processed_img,(5,5),0)
    verts = np.array([[10,500],[10,300],[300,200],[500,200],[800,300],[800,500]])
    processed_img = roi(processed_img,[verts])

    # read Houghlines
    # needs to be edges
    lines = cv2.HoughLinesP(processed_img, 1, np.pi/180, 180, 20, 15)
    draw_lines(processed_img, lines)

    return processed_img


def main():
    for i in list(range(4))[::-1]:
        print(i+1)
        time.sleep(1)

    lst = time.time()
    while(True):
        screen_pil = np.array(sct.grab((0,40,800,640)))
        new_screen = process_img(screen_pil)
        print("Loop took {}".format((time.time()-lst)))
        lst = time.time()
        cv2.imshow("window", new_screen)
        # cv2.imshow("image", screen_pil)
        if cv2.waitKey(25) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            break

if __name__ == '__main__':
    main()
