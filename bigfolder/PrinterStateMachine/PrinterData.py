from opcua import Client


class PrinterData:
    def __init__(self, printer_number, api_key=''):
        """
        All the nodes you could ever need.
        :param printer_number: Starts with 0.
        :param api_key: the octo print api key.
        """
        self.nodes_dict = {
            "state_node": f"ns={11 + printer_number};s=P{printer_number + 1}d_State",
            "start_node": f"ns={11 + printer_number};s=P{printer_number + 1}c_Start",
            "part_removed_node": f"ns={11 + printer_number};s=P{printer_number + 1}c_PartRemoved",
            "ready_node": f"ns={11 + printer_number};s=P{printer_number + 1}f_Ready",
            "bed_temp_node": f"ns={11 + printer_number};s=P{printer_number + 1}d_tBedReal",
            "bed_temp_target": f"ns={11 + printer_number};s=P{printer_number + 1}d_tBedTarget",
            "noz_temp_node": f"ns={11 + printer_number};s=P{printer_number + 1}d_tNozReal",
            "noz_temp_target": f"ns={11 + printer_number};s=P{printer_number + 1}d_tNozTarget",
            "end_node": f"ns={11 + printer_number};s=P{printer_number + 1}f_End",
            "filename_node": f"ns={11 + printer_number};s=P{printer_number + 1}c_File",
            "job_file_node": f"ns={11 + printer_number};s=P{printer_number + 1}d_JobFile",
            "job_progress_node": f"ns={11 + printer_number};s=P{printer_number + 1}d_JobProgress",
            "job_time_node": f"ns={11 + printer_number};s=P{printer_number + 1}d_JobTime",
            "job_time_left_node": f"ns={11 + printer_number};s=P{printer_number + 1}d_JobTimeLeft",
            "job_estimated_time_node": f"ns={11 + printer_number};s=P{printer_number + 1}d_JobTimeEst",
            "prog_id_node": f"ns={11 + printer_number};s=P{printer_number + 1}c_ProgID",
            "x_jog_node": f"ns={11 + printer_number};s=P{printer_number + 1}c_JogX",
            "y_jog_node": f"ns={11 + printer_number};s=P{printer_number + 1}c_JogY",
            "z_jog_node": f"ns={11 + printer_number};s=P{printer_number + 1}c_JogZ",
            "api_resp_node": f"ns={11 + printer_number};s=P{printer_number + 1}d_APIresp"
        }

        self.plate_empty = True
        self.octo_state = ""
        self.base_url = f'http://172.31.1.22{5 + printer_number}:5000/api/'
        self.stream_url = f"http://172.31.1.22{5 + printer_number}:8080/?action=stream"
        self.api_key = api_key
        self.headers = {
            'X-Api-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        self.client_address = 'oct.tpc://172.31.1.236:4840/server/'
        self.my_client = Client(self.client_address)
        self.my_client.connect()

    def get_node_address(self, node_name) -> str:
        """
        Returns a node address from the nodes_dict.
        :param node_name: the name of the node
        :return: the node address, as a string.
        """
        return self.nodes_dict[node_name]

    def node_value_change(self, node_name: str, value):
        """
        Changes the value of a node in the OPCUA server.
        :param node_name: The name of the node to change.
        :param value:
        :return:
        """
        node_address = self.nodes_dict[node_name]
        node = self.my_client.get_node(node_address)
        v_type = node.get_data_type_as_variant_type()
        node.set_value(value, v_type)

    def node_value_get(self, node_name: str):
        node_address = self.nodes_dict[node_name]
        node = self.my_client.get_node(node_address)
        return node.get_value()





