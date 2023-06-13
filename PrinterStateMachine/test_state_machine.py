import json
import time

import requests
from statemachine import StateMachine, State
from statemachine.exceptions import TransitionNotAllowed
from PrinterData import PrinterData


class PrinterStateMachine(StateMachine):
    operational = State('Operational', initial=True)
    heating = State('Heating')
    printing = State('Printing')
    cancel = State('Cancelling')
    # cooldown = State('Cooldown')
    part_on_bed = State('Part on Bed')

    heat = operational.to(heating)
    print = heating.to(printing)
    print_done = printing.to(part_on_bed)
    part_removed = part_on_bed.to(operational)

    cancel_job = (printing.to(cancel) | heating.to(cancel))
    exit_cancel = (cancel.to(operational, cond="is_plate_empty") | cancel.to(part_on_bed, unless="is_plate_empty"))

    def __init__(self, p_data: PrinterData):
        self.p_data = p_data
        super().__init__()

    def on_enter_state(self):
        print(f"State changed to: {self.current_state_value}")
        self.p_data.node_value_change("state_node", self.current_state_value)

    def on_enter_heating(self):
        filename = self.p_data.node_value_get("filename_node")
        payload = {'command': 'select', 'print': 'true'}
        url = self.p_data.base_url + 'files/local/' + filename
        print(url)
        response = requests.post(url, headers=self.p_data.headers, params=payload, data=json.dumps(payload))
        print(response)

    def on_enter_cooldown(self):
        print("we are now cooling down")
        self.p_data.node_value_change("end_node", True)

    def on_enter_operational(self):
        self.p_data.plate_empty = True
        self.p_data.node_value_change("part_removed_node", False)
        self.p_data.node_value_change("ready_node", True)

    def on_exit_operational(self):
        self.p_data.node_value_change("ready_node", False)

    def on_enter_printing(self):
        self.p_data.plate_empty = False

    def on_enter_part_on_bed(self):
        self.head_jog(0, 0, 30)

    def on_enter_cancel(self):
        job_payload = {'command': 'cancel'}
        url = self.p_data.base_url + 'job'
        response = requests.post(url, headers=self.p_data.headers, params=job_payload, data=json.dumps(job_payload))
        print(response)

        # Giving the Printer some time to cancel the job.
        time.sleep(2)
        # Blocking if the Printer is still in the Cancelling state (octo state, not my state).
        while self.p_data.octo_state == "Cancelling":
            pass
        self.exit_cancel()

    def check_heating(self):
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
        self.p_data.node_value_change("start_node", False)
        prog_id = self.p_data.node_value_get("prog_id_node")
        if prog_id == 1:
            self.heat()
        elif prog_id == 2:
            self.cancel_job()
        elif prog_id == 3:
            self.head_jog(x=self.p_data.node_value_get("x_jog_node"),
                          y=self.p_data.node_value_get("y_jog_node"),
                          z=self.p_data.node_value_get("z_jog_node"))
        else:
            print(f"Program ID is {prog_id}, I don't know what to do with that.")

    def head_jog(self, x, y, z):
        payload = {'command': 'jog', 'x': x, 'y': y, 'z': z}
        url = self.p_data.base_url + 'printer/printhead'
        response = requests.post(url, headers=self.p_data.headers, params=payload, data=json.dumps(payload))
        print(response)

    def is_plate_empty(self):
        return self.p_data.plate_empty
