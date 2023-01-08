class Resource:
    def __init__(self, rsrc_id: str):
        self.prog_id: int = 0
        self.start: bool = False
        self.ready: bool = True
        self.end: bool = False
        self.rsrc_id = rsrc_id
        self.task_id = ""

    def busy(self) -> bool:
        return self.task_id != ""


class Printer(Resource):
    def __init__(self, rsrc_id: str):
        super().__init__(rsrc_id)
        self.state = ""  # Get this from Keenan (state diagram)


class Robot(Resource):
    def __init__(self, rsrc_id: str):
        super().__init__(rsrc_id)


class InspectionStation(Resource):
    def __init__(self, rsrc_id: str):
        super().__init__(rsrc_id)
