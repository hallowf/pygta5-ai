import keyboard

class TKI(object):
    """docstring for TKI."""

    def __init__(self):
        super(TKI, self).__init__()
        keyboard.add_hotkey("ctrl+q", self.do_quit, args=[])
        self.quit = False

    def do_quit(self):
        self.quit = True

    def test_key_input(self):
        while True:
            if self.quit:
                break
            else:
                if keyboard.is_pressed("w+a"):
                    print("wa")
                elif keyboard.is_pressed("a"):
                    print("a")
                elif keyboard.is_pressed("w+d"):
                    print("wd")
                elif keyboard.is_pressed("d"):
                    print("d")
                elif keyboard.is_pressed("w"):
                    print("w")
                else:
                    print("None")

if __name__ == '__main__':
    TKI().test_key_input()
