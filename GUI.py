import tkinter as tk
import threading


class App(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def callback(self):
        self.root.quit()

    def run(self):
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.callback)
        self.window_inject()
        self.root.mainloop()

    def window_inject(self):
        label = tk.Label(self.root, text="OPCUA Mimicker")
        label.pack()


class GUI:
    def __init__(self):
        self.app = App()
