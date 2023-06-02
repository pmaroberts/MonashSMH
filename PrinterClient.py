import threading
import time

import requests
from opcua import *
from test_state_machine import PrinterStateMachine
from NodeListener import *
from test_state_machine import node_value_change, node_value_get

base_url = 'http://172.31.1.225:5000/api/'
api_key = 'AAA66DA914D847FF91CC48A8080B4D1C'
headers = {
    'X-Api-Key': api_key,
    'Content-Type': 'application/json'
}


def bind_nodes(my_client: Client, node_addresses: list[str], handler: object):
    """
    This method subscribes the handler to the node. Whenever the node changes state,
    the handler will run its datachange_notification method.
    :param my_client: A connected opcua Client object
    :param node_addresses: list of node addresses to subscribe to
    :param handler: A class with a datachange_notification method to handle changes
    :return: None.
    """
    # print('i ran')
    nodes = [my_client.get_node(addr) for addr in node_addresses]
    my_handler = handler
    my_sub = my_client.create_subscription(500, my_handler)
    handle = my_sub.subscribe_data_change(nodes)


class PrinterClient:
    def __init__(self, printer_number):
        self.nodes_dict = {
            "state_node": f"ns={11 + printer_number};s=P{printer_number + 1}d_State",
            "file_node": f"ns={11 + printer_number};s=P{printer_number + 1}c_File",
            "start_node": f"ns={11 + printer_number};s=P{printer_number + 1}c_Start",
            "part_removed_node": f"ns={11 + printer_number};s=P{printer_number + 1}c_PartRemoved",
            "ready_node": f"ns={11 + printer_number};s=P{printer_number + 1}f_Ready",
            "bed_temp_node": f"ns={11 + printer_number};s=P{printer_number + 1}d_tBedReal",
            "noz_temp_node": f"ns={11 + printer_number};s=P{printer_number + 1}d_tNozReal",
            "end_node": f"ns={11 + printer_number};s=P{printer_number + 1}f_End",
            "filename_node": f"ns={11 + printer_number};s=P{printer_number + 1}c_File",
            "client_address": 'oct.tpc://172.31.1.236:4840/server/'
        }
        self.my_client = Client(self.nodes_dict['client_address'])
        self.state_machine = PrinterStateMachine(self.nodes_dict)

    def run_printer(self):
        try:
            self.my_client.connect()
        except Exception as e:
            print(e)
            print("not a slay")
        else:
            bind_nodes(self.my_client, [self.nodes_dict["start_node"]], StartHandler(self.state_machine))
            # bind_nodes(self.my_client, [self.nodes_dict["bed_temp_node"]], BedTempHandler(self.state_machine))
            # bind_nodes(self.my_client, [self.nodes_dict["noz_temp_node"]], NozTempHandler(self.state_machine))
            # bind_nodes(self.my_client, [self.nodes_dict["end_node"]], EndHandler(self.state_machine))
            bind_nodes(self.my_client, [self.nodes_dict["part_removed_node"]], PartRemovedHandler(self.state_machine))

    def update_printer(self):
        while True:
            response = requests.get(base_url + 'printer', headers=headers).json()
            self.state_machine.set_bed_temp(response['temperature']['bed']['actual'])
            self.state_machine.set_noz_temp(response['temperature']['tool0']['actual'])
            print(response['state']['text'])
            if response['state']['flags']['finishing']:
                self.state_machine.print_done()
            # print(f"Bed: {self.state_machine.bed_temp}, Nozzle: {self.state_machine.noz_temp}")
            time.sleep(1)


if __name__ == '__main__':
    printer2 = PrinterClient(0)
    thread_one = threading.Thread(target=printer2.run_printer)
    thread_two = threading.Thread(target=printer2.update_printer)
    thread_one.start()
    thread_two.start()
