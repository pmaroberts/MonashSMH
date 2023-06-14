import sys
import threading
import time
from datetime import datetime
import requests
from PrinterData import PrinterData
from NodeListener import *
from test_state_machine import PrinterStateMachine


class PrinterClient:
    def __init__(self, printer_number, api_key):
        self.p_data = PrinterData(printer_number, api_key)
        self.my_client = Client(self.p_data.client_address)
        self.state_machine = PrinterStateMachine(self.p_data)

    def run_printer(self):
        """
        This function runs in the first thread. It is used to listen to the OPCUA server for nodes that
        are bound, at the moment these are "start" and "part_removed".
        :return:
        """
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
        """
        This function runs in the second thread. It is used to update the OPCUA server with the current state of the
        printer. It is a while loop, polling the printer status every second.
        :return:
        """
        while True:
            self.check_printer()
            if self.state_machine.current_state_value == "printing":
                self.check_job()
            time.sleep(1)
            # os.system('cls')

    def check_printer(self):
        """
        Calls the API to get the current state of the printer. It then updates the OPCUA server with the new values.
        :return: None
        """
        # API call to the printer
        response = requests.get(self.p_data.base_url + 'printer', headers=self.p_data.headers).json()
        print(f"OctoState is {response['state']['text']} at {datetime.now().strftime('%H:%M:%S')}")
        self.p_data.node_value_change("bed_temp_node", response['temperature']['bed']['actual'])
        self.p_data.node_value_change("bed_temp_target", response['temperature']['bed']['target'])
        self.p_data.node_value_change("noz_temp_node", response['temperature']['tool0']['actual'])
        self.p_data.node_value_change("noz_temp_target", response['temperature']['tool0']['target'])
        self.p_data.octo_state = response['state']['text']
        # This line asks the state machine if it is ready to advance to the "print" state
        self.state_machine.check_heating()

    def check_job(self):
        """
        Prints the current job progress to the console. It also updates the OPCUA server with the current job progress.
        If the job progress reaches 100, the state machine is told to advance to the "part_on_bed" state.
        :return: None
        """
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


class StartHandler(Handler):
    def __init__(self, state_machine: PrinterStateMachine):
        self.state_machine = state_machine

    def datachange_notification(self, node, val, data):
        if val:
            self.state_machine.start_handler()


class PartRemovedHandler(Handler):
    def __init__(self, state_machine: PrinterStateMachine):
        self.state_machine = state_machine

    def datachange_notification(self, node, val, data):
        if val:
            self.state_machine.part_removed()


def main():
    """
    Main function to run the program. It takes a command line argument to determine which printer to connect to.
    NOTE: Index counting. Printer 1 is zero.
    :return: None
    """
    if len(sys.argv) < 2:
        print("Usage: python PrinterClient.py <value>")
        sys.exit(1)

    value = int(sys.argv[1])

    api_key = ['26F256BD5B564A6B87FA1710B4D6914E', 'DDFFC3AB00B9444BA96250E437831B70']

    printer2 = PrinterClient(value, api_key[value])

    thread_one = threading.Thread(target=printer2.run_printer, daemon=True)
    thread_two = threading.Thread(target=printer2.update_printer, daemon=True)

    thread_one.start()
    thread_two.start()


if __name__ == '__main__':
    main()
