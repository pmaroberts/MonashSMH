import asyncio

from asyncua import Client

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

    def get_state(self) -> None:
        """
        This method allows someone to mimic the OPCUA through the console.
        :param opcua:
        :return: None
        """
        # pass
        print(f"\033[1;32m\nSetting state for {self.rsrc_id}. Current state is '{self.states[self.state]}'")
        i: int = 0
        for state in self.states:
            print(f"To set state to {state} press {i}.")
            i += 1
        print(f"To leave in current state ({self.states[self.state]}), press enter.")
        inputted_state = input("Enter your input here: ")
        try:
            int(inputted_state)
        except ValueError:
            print("\nState not changed.\033[1;00m")
            return None

        if int(inputted_state) in range(len(self.states)):
            self.state = int(inputted_state)
        print(f"State changed to {inputted_state}\033[1;00m")
        return None

    def upon_task_completion(
            self) -> None:  # Can inherit this method in order to create a cleaning cycle for printer etc.
        """
        This method runs when a task completes. The default is to set the state back to ready.
        :return: None
        """
        self.state = 0

    def part_pickup_handler(self) -> None:
        """
        This method tells is called to tell the resource that a part has been picked up from its location.
        :return: None
        """
        pass

    def set_to_default_working_state(self):
        self.state = 1


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
        self.state_node = ""
        self.state = "Default"

        # self.states = ["ready", "printing", "finished printing", "bed empty, not ready"]

    def upon_task_completion(self) -> None:
        """
        This method sets state to 'finished printing', not ready. The part is still on the bed.
        :return: None
        """
        self.state = "Part on Bed"
        asyncio.get_event_loop().run_until_complete(OPCUA.set_data(self.state_node, self.state))

    def part_pickup_handler(self) -> None:
        """
        This method sets state to 'bed empty, not ready'. The robot has picked up the part.
        :return:
        """
        self.state = "Cleaning Required"
        asyncio.get_event_loop().run_until_complete(OPCUA.set_data(self.state_node, self.state))

    def get_state(self) -> None:
        print(f"{self.rsrc_id} is in state {self.state}")
        self.state = asyncio.get_event_loop().run_until_complete(OPCUA.get_data(self.state_node))
        print(f"{self.rsrc_id} now in state {self.state}")

    def set_to_default_working_state(self):
        asyncio.get_event_loop().run_until_complete(OPCUA.set_data(self.state_node, "Printing"))


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
        self.state = "Ready"
        self.states = ["Ready", "Busy", "Done"]
        self.ready_node = ""
        self.end_node = ""
        self.start_node = ""
        self.prog_id_node = ""
        self.prog_id = 69

    def set_to_default_working_state(self):
        # Use this method to set the program ID
        self.state = "Busy"
        asyncio.get_event_loop().run_until_complete(OPCUA.set_data(self.start_node, True))
        asyncio.get_event_loop().run_until_complete(OPCUA.set_data(self.prog_id_node, self.prog_id))
        asyncio.get_event_loop().run_until_complete(OPCUA.set_data(self.ready_node, False))
        asyncio.get_event_loop().run_until_complete(OPCUA.set_data(self.end_node, False))

    def get_state(self) -> None:
        print(f"{self.rsrc_id} is in state {self.state}")
        ready = asyncio.get_event_loop().run_until_complete(OPCUA.get_data(self.ready_node))
        end = asyncio.get_event_loop().run_until_complete(OPCUA.get_data(self.end_node))
        if eval(ready):
            self.state = "Ready"
        elif eval(end):
            self.state = "Done"
            asyncio.get_event_loop().run_until_complete(OPCUA.set_data(self.prog_id_node, self.prog_id))
        print(f"{self.rsrc_id} is now in state {self.state}")

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
        self.states = ["ready", "busy", "done", "failed"]