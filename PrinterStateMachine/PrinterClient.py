import os
import sys
import threading
import time
from datetime import datetime
import requests
from opcua import *
from PrinterData import PrinterData
from NodeListener import *


def bind_nodes(my_client: Client, node_addresses: list[str], handler: object):
    """
    This method subscribes the handler to the node. Whenever the node changes state,
    the handler will run its datachange_notification method.
    :param my_client: A connected opcua Client object
    :param node_addresses: list of node addresses to subscribe to
    :param handler: A class with a datachange_notification method to handle changes
    :return: None.
    """
    nodes = [my_client.get_node(addr) for addr in node_addresses]
    my_handler = handler
    my_sub = my_client.create_subscription(500, my_handler)
    handle = my_sub.subscribe_data_change(nodes)


class PrinterClient:
    def __init__(self, printer_number, api_key):
        self.p_data = PrinterData(printer_number, api_key)
        self.my_client = Client(self.p_data.client_address)
        self.state_machine = PrinterStateMachine(self.p_data)

    def run_printer(self):
        try:
            self.my_client.connect()
        except Exception as e:
            print(e)
            print("not a slay")
        else:
            bind_nodes(self.my_client, [self.p_data.get_node_address("start_node")], StartHandler(self.state_machine))
            bind_nodes(self.my_client, [self.p_data.get_node_address("part_removed_node")],
                       PartRemovedHandler(self.state_machine))

    def update_printer(self):
        while True:
            self.check_printer()
            if self.state_machine.current_state_value == "printing":
                self.check_job()
            time.sleep(1)
            # os.system('cls')

    def check_printer(self):
        # API call to the printer
        response = requests.get(self.p_data.base_url + 'printer', headers=self.p_data.headers).json()
        print(f"{response['state']['text']} at {datetime.now().strftime('%H:%M:%S')}")
        self.p_data.node_value_change("bed_temp_node", response['temperature']['bed']['actual'])
        self.p_data.node_value_change("bed_temp_target", response['temperature']['bed']['target'])
        self.p_data.node_value_change("noz_temp_node", response['temperature']['tool0']['actual'])
        self.p_data.node_value_change("noz_temp_target", response['temperature']['tool0']['target'])
        self.p_data.octo_state = response['state']['text']
        self.state_machine.check_heating()

    def check_job(self):
        # API call to ther job
        response = requests.get(self.p_data.base_url + 'job', headers=self.p_data.headers).json()
        progress = response['progress']['completion']
        self.p_data.node_value_change("job_file_node", response['job']['file']['name'])
        self.p_data.node_value_change("job_progress_node", progress)
        self.p_data.node_value_change("job_time_node", response['progress']['printTime'])
        self.p_data.node_value_change("job_time_left_node", response['progress']['printTimeLeft'])
        self.p_data.node_value_change("job_estimated_time_node", response['job']['estimatedPrintTime'])
        if progress == 100:
            self.state_machine.print_done()
        print(f"job is {response['progress']['completion']} complete")


if __name__ == '__main__':
    # if len(sys.argv) < 2:
    #     print("Usage: python your_script.py <value>")
    #     sys.exit(1)
    #
    # value = int(sys.argv[1])
    value = 0
    api_key = '26F256BD5B564A6B87FA1710B4D6914E'
    api_key2 = 'DDFFC3AB00B9444BA96250E437831B70'
    printer2 = PrinterClient(value, api_key)

    thread_one = threading.Thread(target=printer2.run_printer)
    thread_two = threading.Thread(target=printer2.update_printer)

    thread_one.start()
    thread_two.start()
