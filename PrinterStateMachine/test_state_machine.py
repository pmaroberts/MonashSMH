import json
import time
import requests
from statemachine import StateMachine, State
from statemachine.exceptions import TransitionNotAllowed
from PrinterData import PrinterData


class PrinterStateMachine(StateMachine):
    """
    This class is a state machine for the printer. It is used to track the state of the printer.
    """

    # The States for the Printer
    operational = State('Operational', initial=True)
    heating = State('Heating')
    printing = State('Printing')
    cancel = State('Cancelling')
    part_on_bed = State('Part on Bed')

    # The Transitions for the Printer, under normal conditions
    heat = operational.to(heating)
    print = heating.to(printing)
    print_done = printing.to(part_on_bed)
    part_removed = part_on_bed.to(operational)

    # The Transitions for the Printer for cancelling.
    cancel_job = (printing.to(cancel) | heating.to(cancel))
    exit_cancel = (cancel.to(operational, cond="is_plate_empty") | cancel.to(part_on_bed, unless="is_plate_empty"))

    def __init__(self, p_data: PrinterData):
        """
        Constructor for the PrinterStateMachine class.
        :param p_data: A PrinterData object used for handling the Printer's individual Data
        """
        self.p_data = p_data
        super().__init__()

    def on_enter_state(self):
        """
        Print every state change to console. Also update the OPCUA server.
        :return: None
        """
        print(f"State changed to: {self.current_state_value}")
        self.p_data.node_value_change("state_node", self.current_state_value)

    def on_enter_heating(self):
        """
        When we heat, we want to make an API call to get the Printer printing.
        :return: None
        """
        filename = self.p_data.node_value_get("filename_node")
        payload = {'command': 'select', 'print': 'true'}
        url = self.p_data.base_url + 'files/local/' + filename
        print(url)
        response = requests.post(url, headers=self.p_data.headers, params=payload, data=json.dumps(payload))
        print(response)
        self.p_data.node_value_change("api_resp_node", str(response.status_code))

        if response.status_code != 204:
            print("Error: Could not start print job. Canceling.")
            self.cancel_job()

    def on_enter_operational(self):
        """
        When we enter operational, the plate should be empty, the part should be removed, and the printer should be ready.
        :return: None
        """
        self.p_data.plate_empty = True
        self.p_data.node_value_change("part_removed_node", False)
        self.p_data.node_value_change("ready_node", True)
        self.p_data.node_value_change("api_resp_node", "")

    def on_exit_operational(self):
        """
        If we exit operational, the printer is no longer ready.
        :return:
        """
        self.p_data.node_value_change("ready_node", False)

    def on_enter_printing(self):
        """
        Upon entering the printing state, the plate is no longer empty.
        :return:
        """
        self.p_data.plate_empty = False

    def on_enter_part_on_bed(self):
        """
        When we get to part on bed, we should raise the head by 3 cm.
        :return:
        """
        self.p_data.node_value_change("job_file_node", '')
        self.p_data.node_value_change("job_progress_node", 0)
        self.p_data.node_value_change("job_time_node", 0)
        self.p_data.node_value_change("job_time_left_node", 0)
        self.p_data.node_value_change("job_estimated_time_node", 0)
        self.head_jog(x=0, y=0, z=30)

    def on_enter_cancel(self):
        """
        Cancels the current job when we enter cancel.
        :return:
        """
        job_payload = {'command': 'cancel'}
        url = self.p_data.base_url + 'job'
        response = requests.post(url, headers=self.p_data.headers, params=job_payload, data=json.dumps(job_payload))
        print(response)
        self.p_data.node_value_change("api_resp_node", str(response.status_code))

        # Giving the Printer some time to cancel the job.
        time.sleep(2)
        # Blocking if the Printer is still in the Cancelling state (octo state, not my state).
        while self.p_data.octo_state == "Cancelling":
            pass
        self.exit_cancel()

    def check_heating(self):
        """
        Checks the temperature of the bed and nozzle. If they are within delta degrees of the target, it will start printing.
        :return:
        """
        # Delta is the amount of degrees the bed and nozzle can be off by before state change to printing.
        delta = 2
        # Get the current temperature of the bed and nozzle
        noz = self.p_data.node_value_get("noz_temp_node")
        bed = self.p_data.node_value_get("bed_temp_node")
        noz_target = self.p_data.node_value_get("noz_temp_target")
        bed_target = self.p_data.node_value_get("bed_temp_target")

        # Change from printing to heating. If the targets are zero, it hasn't updated.
        if self.current_state_value == "heating":
            if bed_target != 0 and noz_target != 0:
                if bed >= bed_target - delta and noz >= noz_target - delta:
                    try:
                        self.print()
                    except TransitionNotAllowed:
                        # print('transition not allowed')
                        pass

    def start_handler(self):
        """
        This function is called when the start flag is raised. It will call the appropriate function based on the program ID.
        :return: None
        """
        self.p_data.node_value_change("start_node", False)
        prog_id = self.p_data.node_value_get("prog_id_node")
        if prog_id == 1:  # Normal Printing
            self.heat()
        elif prog_id == 2:  # Cancelling
            self.cancel_job()
        elif prog_id == 3:  # Moving the head around.
            self.head_jog(x=self.p_data.node_value_get("x_jog_node"),
                          y=self.p_data.node_value_get("y_jog_node"),
                          z=self.p_data.node_value_get("z_jog_node"))
        else:
            print(f"Program ID is {prog_id}, I don't know what to do with that.")

    def head_jog(self, x, y, z):
        """
        A sneaky little function for changing where the printer head is
        :param x: how much to move in the x direction (mm)
        :param y: how much to move in the y direction (mm)
        :param z: how much to move in the z direction (mm)
        :return: None
        """
        payload = {'command': 'jog', 'x': x, 'y': y, 'z': z}
        url = self.p_data.base_url + 'printer/printhead'
        response = requests.post(url, headers=self.p_data.headers, params=payload, data=json.dumps(payload))
        print(response)
        self.p_data.node_value_change("api_resp_node", str(response.status_code))

    def is_plate_empty(self):
        """
        Quick getter for the plate empty variable. This is done so that we can use the 'cond=' in the state machine for
        cancel.
        :return: True if the plate is empty, false otherwise.
        """
        return self.p_data.plate_empty
