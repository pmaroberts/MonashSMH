class Resource:
    def __init__(self, rsrc_id: str, states: list[str]):
        self.state: int = 0  # All machines should start ready. We can set them to not ready at the start
        self.states: list[str] = states
        self.rsrc_id = rsrc_id
        self.task_id = ""

    def set_state(self):
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
            return

        if int(inputted_state) in range(len(self.states)):
            self.state = int(inputted_state)
        print(f"State changed to {inputted_state}\033[1;00m")

    def upon_task_completion(self):  # Can inherit this method in order to create a cleaning cycle for printer etc.
        self.state = 0


class Printer(Resource):
    def __init__(self, rsrc_id: str):
        super().__init__(rsrc_id, states=["ready", "printing", "finished printing"])

    def upon_task_completion(self):
        self.state = 2  # Set state to finished printing, not ready. The part is still on the bed


class Robot(Resource):
    def __init__(self, rsrc_id: str):
        super().__init__(rsrc_id, states=["ready", "busy", "done"])


class InspectionStation(Resource):
    def __init__(self, rsrc_id: str):
        super().__init__(rsrc_id, states=["ready", "busy", "done", "failed"])
