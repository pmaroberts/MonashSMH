class MES:
    def __init__(self):
        self.resources: dict = {}
        self.executables: dict = {}

    # This method will run 1000s of times, that is the simulation. That is one tick.
    def sys_tick(self, clock: int):
        # Looping the executables and their tasks
        for executable in self.executables.values():
            executable.tick(self, clock)
            for task in executable.tasks:
                task.tick(self, clock)

        # Looping the resources
        for resource in self.resources.values():
            resource.tick(self, clock)

    # This method allows tasks to add themselves to the queue for a resource
    def resource_push(self, rsrc_id: str, task_id: str):
        self.resources[rsrc_id].queue.append(task_id)

    def task_lookup(self, task_id: str):
        id_split = task_id.split('_')
        exec_id = id_split[0]
        try:
            return self.executables[exec_id].task_lookup(task_id)
        except Exception as e:
            print(e)

    def report(self) -> str:
        to_print = ""
        for executable in self.executables.values():
            wait_time = 0
            for task in executable.tasks:
                wait_time += task.wait_time
            to_print += f"{executable.i_d} finished at Time: {executable.done_stamp}. " \
                        f"It waited for {wait_time} ticks.\n"
        return to_print





