import threading
import time
from queue import PriorityQueue, Queue
from typing import List

from BabyMESPackage.TestUploadOctoPrint import upload_file_to_octoprint
from BabyMESPackage.UIVersion1 import GCodeFile
from PrinterStateMachine.PrinterData import PrinterData

COLOR_BLUE = "\033[34m"
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[32m"


class PrintJob:
    def __init__(self, filename, filepath, priority=1):
        self.filename = filename
        self.filepath = filepath
        self.priority = priority

    def __lt__(self, other):
        return self.priority > other.priority


class BabyMES:

    def __init__(self):
        self.queue = Queue()
        self.printers = []
        self.printers.append(PrinterData(0))
        self.printers.append(PrinterData(1))
        self.lock = threading.Lock()

    def print_queue(self) -> str:
        with self.lock:
            output = COLOR_GREEN + "Queue: "
            if not self.queue.empty():
                list_of_queue = list(self.queue.queue)
                for job in list_of_queue:
                    output += job.filename + ', '
            else:
                output += "Empty"
            return output + COLOR_RESET

    def on_state_change(self, printer_number, state):
        if state == "operational":
            self.start_print(printer_number)
        elif state == 'part_on_bed':
            print(f'\n{COLOR_BLUE}System Message: PICKUP NEEDED ON {printer_number}{COLOR_RESET}')

    def start_print(self, printer_number):
        with self.lock:
            if self.queue.empty():
                pass
                # print(f'\nSystem Message: NO JOBS IN QUEUE')
            else:
                job = self.queue.get()
                if not self.upload_file_mvp(printer_number, job):
                    return
                initial_api = ""
                self.printers[printer_number].node_value_change("api_resp_node", initial_api)
                self.printers[printer_number].node_value_change("filename_node", job.filename)
                self.printers[printer_number].node_value_change("prog_id_node", 1)
                self.printers[printer_number].node_value_change("start_node", True)
                while self.printers[printer_number].node_value_get("api_resp_node") == initial_api:
                    pass  # Wait for the API to respond
                if self.printers[printer_number].node_value_get("api_resp_node") != '204':
                    print(f"{COLOR_BLUE}Error: Could not start print job. Canceling.{COLOR_RESET}")
                else:
                    print(f'{COLOR_BLUE}System Message: Starting {job.filename} on Printer {printer_number}{COLOR_RESET}')
                self.printers[printer_number].node_value_change("api_resp_node", "")

    def upload_file_mvp(self, printer_number: int, job: PrintJob) -> bool:
        return upload_file_to_octoprint(filePath=job.filepath, printerNumber=printer_number+1)

    def batch_add(self, to_add_list: List[GCodeFile]):
        for item in to_add_list:
            qty = item.quantity
            filename = item.filename
            filepath = item.file_path
            for _ in range(qty):
                self.push_part_to_queue(filename=filename, filepath=filepath, priority=1, straight_away=False)

    def push_part_to_queue(self, filename, filepath, priority, straight_away=True):
        with self.lock:
            # Add to the queue
            self.queue.put(PrintJob(filename=filename, filepath=filepath, priority=priority))
            # See if there are any printers we can give this job to straight away
            if straight_away:
                self.force_start_print()

    def force_start_print(self):
        for i in range(len(self.printers)):
            if self.printers[i].node_value_get("state_node") == 'operational':
                if not self.queue.empty():
                    self.start_print(i)
                else:
                    return

    def add_part_from_console(self):
        filename = input("Enter filename (should end in .gcode): ")
        priority = input("Enter priority (should be an integer, higher will print first): ")
        if filename:
            self.push_part_to_queue(filename, priority)
        else:
            print('No file entered')

    def register_pickup(self, printer_number):
        self.printers[printer_number].node_value_change("part_removed_node", True)

    def register_pickup_from_console(self):
        printer_number = int(input("Enter printer number for which you have cleared the bed: "))
        try:
            self.register_pickup(printer_number)
        except IndexError:
            print(f'{COLOR_BLUE}Error: Printer {printer_number} does not exist{COLOR_RESET}')

    def cancel_printer_job(self, printer_number):
        self.printers[printer_number].node_value_change("prog_id_node", 2)
        self.printers[printer_number].node_value_change("start_node", True)
        print(f'{COLOR_BLUE}System Message: Canceling job on Printer {printer_number}{COLOR_RESET}')

    def cancel_printer_job_from_console(self):
        printer_number = int(input("Enter printer number for which you want to cancel the job: "))
        try:
            self.cancel_printer_job(printer_number)
        except IndexError:
            print(f'{COLOR_BLUE}Error: Printer {printer_number} does not exist{COLOR_RESET}')

    def display_menu(self):
        print("\nBabyMES Command Menu")
        print(f"{self.print_queue()}")
        print("1. Add a print job")
        print("2. Register a pickup as completed")
        print("3. Cancel a job on a printer")
        print("4. Refresh")
        print("5. Force Start Print")

    def process_command(self, command):
        if command == '1':
            self.add_part_from_console()
        elif command == '2':
            self.register_pickup_from_console()
        elif command == '3':
            self.cancel_printer_job_from_console()
        elif command == '4':
            pass
        elif command == '5':
            self.force_start_print()
        else:
            print("Invalid command. Please try again.")

    def run(self):
        while True:
            self.display_menu()
            command = input("Enter command: ")
            self.process_command(command)
