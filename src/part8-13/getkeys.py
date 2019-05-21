# Citation: Box Of Hats (https://github.com/Box-Of-Hats )

import win32api as wapi
import time

keyList = ["\b", ""]
key_list = ["space"]
for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789":
    keyList.append(char)
    key_list.append(char.lower())



def key_check():
    keys = []
    for key in keyList:
        if wapi.GetAsyncKeyState(ord(key)):
            keys.append(key)
    return keys

def keyboard_check():
    keys = []
    for key in key_list
        if keyboard.is_pressed(key):
            keys.append(key)
    return keys
