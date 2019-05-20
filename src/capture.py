import mss
import cv2

def main():
    for i in list(range(4))[::-1]:
        print(i+1)
        time.sleep(1)

    lst = time.time()
    while(True):
        screen_pil = np.array(sct.grab((0,40,800,640)))
        print("Loop took {}".format((time.time()-lst)))
        lst = time.time()
        cv2.imshow("image", screen_pil)
        if cv2.waitKey(25) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            break

if __name__ == '__main__':
    main()
