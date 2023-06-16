import sys
from threading import Thread

from PyQt5.QtWidgets import QApplication
from opcua import Client

from BabyMESPackage.BabyMES import BabyMES
from BabyMESPackage.UIVersion1 import MainWindow
from PrinterStateMachine.NodeListener import bind_nodes, Handler
from baby_mes_ui.PrinterWidget import PrinterWidget


class StateHandler(Handler):

    def __init__(self, baby_mes: BabyMES = None):
        self.baby_mes = baby_mes

    def datachange_notification(self, node, val, data):
        node_address = str(node)
        p_index = node_address.find('P')
        d_index = node_address.find('d')
        # Extract the substring between 'P' and 'd'
        printer_number_str = node_address[p_index + 1: d_index]

        # Convert the extracted substring to an integer
        printer_number = int(printer_number_str)
        # print(f'Printer {printer_number} changed state to {val}')
        if self.baby_mes:
            self.baby_mes.on_state_change(printer_number - 1, val)


class BabyMESRunner:
    def __init__(self):
        self.baby_mes = BabyMES()
        self.my_client = Client(self.baby_mes.printers[0].client_address)

    def run_input_gui(self):
        app = QApplication(sys.argv)

        window = MainWindow()
        window.order_now_signal.connect(self.baby_mes.batch_add)
        window.show()

        sys.exit(app.exec_())

    def listen_for_printers(self):
        try:
            self.my_client.connect()
        except Exception as e:
            print(e)
            print("not a slay")
        else:
            for printer in self.baby_mes.printers:
                bind_nodes(self.my_client, [printer.get_node_address("state_node")], StateHandler(self.baby_mes))


def main():
    bmr = BabyMESRunner()
    bmr.listen_for_printers()

    mes_thread = Thread(target=bmr.baby_mes.run, daemon=True)
    input_gui_thread = Thread(target=bmr.run_input_gui, daemon=True)

    mes_thread.start()
    input_gui_thread.start()


if __name__ == '__main__':
    main()
