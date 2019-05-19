import time
import keyboard

for i in list(range(4))[::-1]:
    print(i+1)
    time.sleep(1)

keyboard.press("w")
time.sleep(3)
keyboard.release("w")
