import asyncio
from OPCUAInterface import OPCUA


class Resource:
    """
    This is a class to represent manufacturing resources (machines in the system)

    Attributes:
        state (int): an integer state for the machine (would come from the OPCUA in future).
                     Convention: 0 represents ready, 1 represents busy and 2 represents done.
        states (list[str]): A list of descriptive words corresponding to each of the integer states.
                            e.g. ["ready", "printing", "finished printing"]
        rsrc_id (str): the string id of the resource.
        task_id (str): the string id of the task that the machine is working on

    """

    def __init__(self, rsrc_id: str):
        """
        Constructor for the resource class.
        :param rsrc_id: Resource id is passed through on instantiation
        """
        self.state = 0  # All machines should start ready. We can set them to not ready at the start
        self.states: list[str] = []
        self.rsrc_id = rsrc_id
        self.task_id = ""
        self.ready_node = ""
        self.end_node = ""
        self.start_node = ""
        self.prog_id_node = ""
        self.prog_id = 69

    def get_state(self) -> None:
        pass

    def upon_task_completion(self) -> None:  # Can inherit this method in order to create a cleaning cycle for printer etc.
        """
        This method runs when a task completes. The default is to set the state back to ready.
        :return: None
        """
        pass

    def part_pickup_handler(self) -> None:
        """
        This method tells is called to tell the resource that a part has been picked up from its location.
        :return: None
        """
        pass

    def put_to_work(self, filename=""):
        pass


class Printer(Resource):
    """
    Class to represent printers in the system. Very simple, not a lot of attributes, can be augmented in the future.
    """

    def __init__(self, rsrc_id: str):
        """
        Constructor for the Printer
        :param rsrc_id: Resource id passed through constructor
        The constructor sets the states for the printer
        """
        super().__init__(rsrc_id)
        # The below node address values are set up in the ResourceManager class.
        self.prog_id = 1  # This is the program id for printing
        self.state_node = ""
        self.file_node = ""
        self.part_removed_node = ""
        self.state = ""
        self.prog_id_node = ""

    def part_pickup_handler(self) -> None:
        """
        This method sets the part_removed flag to true.
        :return:
        """
        # self.state = "Cleaning Required"
        self.get_state()
        asyncio.get_event_loop().run_until_complete(OPCUA.set_data(self.part_removed_node, True))

    def get_state(self) -> None:
        # print(f"{self.rsrc_id} is in state {self.state}")
        self.state = asyncio.get_event_loop().run_until_complete(OPCUA.get_data(self.state_node))
        print(f"{self.rsrc_id} is in state {self.state}")

    def put_to_work(self, filename=""):
        # asyncio.get_event_loop().run_until_complete(OPCUA.set_data(self.state_node, "Printing"))
        asyncio.get_event_loop().run_until_complete(OPCUA.set_data(self.file_node, filename))
        asyncio.get_event_loop().run_until_complete(OPCUA.set_data(self.prog_id_node, self.prog_id))
        asyncio.get_event_loop().run_until_complete(OPCUA.set_data(self.start_node, True))


class Robot(Resource):
    """
    Class to represent the Robot.
    """

    def __init__(self, rsrc_id: str):
        """
        Constructor for the Robot.
        :param rsrc_id: Resource id passed through the constructor.
        """
        super().__init__(rsrc_id)
        self.state = "Default"
        self.states = ["Ready", "Busy", "Done"]

    def put_to_work(self, filename=""):
        # Use this method to set the program ID
        self.state = "Busy"
        asyncio.get_event_loop().run_until_complete(OPCUA.set_data(self.start_node, True))
        asyncio.get_event_loop().run_until_complete(OPCUA.set_data(self.prog_id_node, self.prog_id))
        asyncio.get_event_loop().run_until_complete(OPCUA.set_data(self.ready_node, False))
        asyncio.get_event_loop().run_until_complete(OPCUA.set_data(self.end_node, False))

    def get_state(self) -> None:
        # print(f"{self.rsrc_id} is in state {self.state}")
        ready = asyncio.get_event_loop().run_until_complete(OPCUA.get_data(self.ready_node))
        end = asyncio.get_event_loop().run_until_complete(OPCUA.get_data(self.end_node))
        if eval(ready):
            self.state = "Ready"
        elif eval(end):
            self.state = "Done"
            asyncio.get_event_loop().run_until_complete(OPCUA.set_data(self.prog_id_node, self.prog_id))
        print(f"{self.rsrc_id} is in state {self.state}")

    def upon_task_completion(self) -> None:
        self.state = "Default"


class InspectionStation(Resource):
    """
    Class to represent the Inspection Station
    """

    def __init__(self, rsrc_id: str):
        """
        Constructor for the Inspection Station.
        :param rsrc_id:
        """
        super().__init__(rsrc_id)
        self.states = ["Ready", "Busy", "Failed"]
        self.state = "Ready"

    def upon_task_completion(self) -> None:
        self.state = "Ready"

    def put_to_work(self, filename=""):
        self.state = "Busy"
