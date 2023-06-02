import json

import requests
from opcua import Client, Node
from statemachine import StateMachine, State
from statemachine.exceptions import TransitionNotAllowed

from Resource import Printer

base_url = 'http://172.31.1.225:5000/api/'
api_key = 'AAA66DA914D847FF91CC48A8080B4D1C'
headers = {
    'X-Api-Key': api_key,
    'Content-Type': 'application/json'
}


def node_value_change(client: Client, node_address: str, value):
    node = client.get_node(node_address)
    v_type = node.get_data_type_as_variant_type()
    node.set_value(value, v_type)


def node_value_get(client: Client, node_address: str):
    node = client.get_node(node_address)
    return node.get_value()


class PrinterStateMachine(StateMachine):
    operational = State('Operational', initial=True)
    heating = State('Heating')
    printing = State('Printing')
    # cancel = State('Cancelling')
    cooldown = State('Cooldown')
    part_on_bed = State('Part on Bed')
    # cleaning = State('Cleaning Required')
    # maintenance = State('Maintenance')

    heat = operational.to(heating)
    print = heating.to(printing)
    print_done = printing.to(cooldown)
    cooled = cooldown.to(part_on_bed)
    part_removed = part_on_bed.to(operational)

    def __init__(self, node_dict: dict[str, str]):
        self.node_dict = node_dict
        self.client = Client(self.node_dict['client_address'])
        self.client.connect()
        self.bed_temp = node_value_get(self.client, self.node_dict['bed_temp_node'])
        self.noz_temp = node_value_get(self.client, self.node_dict['noz_temp_node'])
        self.bed_target = 60
        self.noz_target = 150
        self.bed_cooled = 59.5
        super().__init__()

    def set_bed_temp(self, temp):
        self.bed_temp = temp
        node_value_change(self.client, self.node_dict['bed_temp_node'], self.bed_temp)
        self.check_heating()

    def set_noz_temp(self, temp):
        self.noz_temp = temp
        node_value_change(self.client, self.node_dict['noz_temp_node'], self.noz_temp)
        self.check_heating()

    def on_enter_state(self):
        print(f"State changed to: {self.current_state_value}")
        node_value_change(self.client, self.node_dict["state_node"], self.current_state_value)

    def on_enter_heating(self):
        # Switch off the start flag
        # Change state to heading in the OPCUA server.
        # print("started heating for printing lol")
        node_value_change(self.client, self.node_dict['start_node'], False)
        filename = node_value_get(self.client, self.node_dict['filename_node'])
        payload = {'command': 'select', 'print': 'true'}
        url = base_url + 'files/local/' + filename
        print(url)
        response = requests.post(url, headers=headers, params=payload, data=json.dumps(payload))
        print(response)

    def on_enter_cooldown(self):
        # print("we are now cooling down")
        node_value_change(self.client, self.node_dict['end_node'], False)

    def on_enter_operational(self):
        node_value_change(self.client, self.node_dict['part_removed_node'], False)

    def check_heating(self):
        if self.noz_temp >= self.noz_target and self.bed_temp >= self.bed_target:
            try:
                self.print()
            except TransitionNotAllowed as e:
                # print(e)
                pass
        elif self.bed_temp <= self.bed_cooled:
            try:
                self.cooled()
            except TransitionNotAllowed as e:
                # print(e)
                pass


if __name__ == '__main__':
    pass
