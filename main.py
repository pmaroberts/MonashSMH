from MESTest import MESTest
import threading


def run():
    mt = MESTest()

    # gui_thread = threading.Thread(target=mt.run_gui())
    run_thread = threading.Thread(target=mt.run(1000))

    run_thread.start()
    # gui_thread.start()

    # gui_thread.join()
    run_thread.join()


if __name__ == '__main__':
    run()
