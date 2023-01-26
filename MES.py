

class MES:
    """
    This is a class for representing the entire manufacturing execution system.

    Attributes:
        resource_managers (dict): Holds the system resources and their ids
        executables (dict): Holds the system executables (jobs and tasks) and their ids
    """

    def __init__(self):
        """
        Constructor for the MES class
        """
        self.resource_managers: dict = {}
        self.executables: dict = {}

    def sys_tick(self, clock: int):
        """
        This is the tick method for the MES system. It ensures that each executable, task and resource's tick method is
        run
        :param clock: Integer to represent where time is up to
        :return: None
        """
        # print(f"\t\t\t CLOCK IS {clock}")
        # Looping the executables and their tasks
        for executable in self.executables.values():
            executable.tick(self, clock)
            for task in executable.tasks:
                task.tick(self, clock)

        # Looping the resources_needed
        for resource in self.resource_managers.values():
            resource.tick(self, clock)

    def resource_push(self, rsrc_id: str, task_id: str):
        """
        This method allows tasks to add themselves (via their task id) to the queue for a resource
        :param rsrc_id: id of the resource the task needs (and is queuing to use)
        :param task_id: id of the task requesting the resource
        :return: None
        """
        self.resource_managers[rsrc_id].queue.append(task_id)

    def resource_release(self, rsrc_id: str):
        self.resource_lookup(rsrc_id).upon_task_completion()

    def task_lookup(self, task_id: str):
        """
        This method allows other classes to search for tasks via their id
        :param task_id: task id of the sought after task
        :return: the task object itself
        """
        try:
            id_split = task_id.split('_')
        except AttributeError:
            return None
        exec_id = id_split[0]
        try:
            return self.executables[exec_id].task_lookup(task_id)
        except Exception as e:
            print(e)

    def resource_lookup(self, rsrc_id: str):
        for manager in self.resource_managers.values():
            for resource in manager.resources:
                if resource.rsrc_id == rsrc_id:
                    return resource

    def report(self) -> str:
        """
        This method generates a simple report of what happened to each task/job in the MES.
        :return: the report in string form
        """
        to_print = ""
        for executable in self.executables.values():
            wait_time = 0
            per_cell_breakdown = ""
            for task in executable.tasks:
                name, task_wait = task.get_wait_time()
                wait_time += task_wait
                per_cell_breakdown += f"{name} waited for {task_wait} ticks.\t"

            to_print += f"{executable.exec_id} finished at Time: {executable.done_stamp}. " \
                        f"It waited for {wait_time} ticks in total: " + per_cell_breakdown + "\n"
        return to_print
