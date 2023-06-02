class PrinterData:
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
        }

        self.base_url = f'http://172.31.1.22{5 + printer_number}:5000/api/'
        self.api_key = 'AAA66DA914D847FF91CC48A8080B4D1C'
        self.headers = {
            'X-Api-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        self.client_address = 'oct.tpc://172.31.1.236:4840/server/'

    def get_node(self, node_name):
        return self.nodes_dict[node_name]
