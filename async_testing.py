# import asyncio
# import random
#
# # ANSI colors
# c = (
#     "\033[0m",  # End of color
#     "\033[36m",  # Cyan
#     "\033[91m",  # Red
#     "\033[35m",  # Magenta
# )
#
#
# async makerandom(idx: int, threshold: int = 6) -> int:
#     print(c[idx + 1] + f"Initiated makerandom({idx}).")
#     i = random.randint(0, 10)
#     while i <= threshold:
#         print(c[idx + 1] + f"makerandom({idx}) == {i} too low; retrying.")
#         await asyncio.sleep(idx + 1)
#         i = random.randint(0, 10)
#     print(c[idx + 1] + f"---> Finished: makerandom({idx}) == {i}" + c[0])
#     return i
#
#
# async main():
#     res = await asyncio.gather(*(makerandom(i, 10 - i - 1) for i in range(3)))
#     return res
#
#
# if __name__ == "__main__":
#     random.seed(444)
#     r1, r2, r3 = asyncio.run(main())
#     print()
#     print(f"r1: {r1}, r2: {r2}, r3: {r3}")
import asyncio
import time

#
# def count():
#     print("One")
#     await asyncio.sleep(1)
#     print("Two")
#
#
# def main():
#     await asyncio.gather(count(), count(), count())
#
#
# if __name__ == "__main__":
#     import time
#
#     s = time.perf_counter()
#     asyncio.run(main())
#     elapsed = time.perf_counter() - s
#     print(f"{__file__} executed in {elapsed:0.2f} seconds.")

import tkinter as tk
import threading


class App(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.start()
        self.word = "fart"

    def callback(self):
        self.root.quit()

    def slay(self):
        self.word = "slay"

    def run(self):
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.callback)

        label = tk.Label(self.root, text="Hello World")
        label.pack()

        button = tk.Button(text="change fart to slay", command=self.slay)
        button.pack()

        self.root.mainloop()


def main():
    app = App()
    print('Now we can continue running code while mainloop runs!')

    for i in range(100000):
        print(app.word)
        time.sleep(1)


if __name__ == "__main__":
    main()
