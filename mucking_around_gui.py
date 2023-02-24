import tkinter as tk

from MES import MES


class MESGUI:
    def __init__(self, mes: MES):
        self.mes = mes
        self.root = tk.Tk()
        self.root.title("MES Viewer")
        self.root.geometry("1500x700")

        self.top = tk.Frame(self.root)
        self.title = tk.Label(self.top, text="MES Viewer", font=("Arial", 20))
        self.top.grid(row=0, column=0, columnspan=20, sticky="N")
        self.title.grid(row=0, column=0)

        self.populate_machine_view()
        self.populate_job_view()

    def populate_machine_view(self):
        machine_view = tk.Frame(self.root)
        machine_view.grid(row=1, column=0, columnspan=10, sticky="N", padx=20)
        tk.Label(machine_view, text="Machine View", font=("Arial", 16)).grid(row=0, column=0, columnspan=10, sticky="N")
        tk.Label(machine_view, text="Machine Type", font=("Arial", 13)).grid(row=1, column=0, sticky="W", padx=10)
        tk.Label(machine_view, text="Machine", font=("Arial", 13)).grid(row=1, column=2, sticky="W", padx=10)
        tk.Label(machine_view, text="Current Task", font=("Arial", 13)).grid(row=1, column=4, sticky="W", padx=10)
        tk.Label(machine_view, text="Queued Tasks", font=("Arial", 13)).grid(row=1, column=6, sticky="W", padx=10)

        managers = list(self.mes.resource_managers.values())
        for i in range(len(managers)):
            tk.Label(machine_view, text=f'{managers[i].rsrc_type}', font=("Arial", 11)).grid(row=i+2, column=0, sticky="W", padx=10)
            print(managers[i].queue)

    def populate_job_view(self):
        job_view = tk.Frame(self.root)
        job_view.grid(row=1, column=10, columnspan=10, sticky="N", padx=20)
        tk.Label(job_view, text="Job View", font=("Arial", 16)).grid(row=0, column=0, columnspan=10, sticky="N")
        tk.Label(job_view, text="Job", font=("Arial", 13)).grid(row=1, column=0, sticky="N", padx=10)
        tk.Label(job_view, text="Part", font=("Arial", 13)).grid(row=1, column=2, sticky="N", padx=10)
        tk.Label(job_view, text="Print", font=("Arial", 13)).grid(row=1, column=4, sticky="N", padx=10)
        tk.Label(job_view, text="Store", font=("Arial", 13)).grid(row=1, column=5, sticky="N", padx=10)
        tk.Label(job_view, text="QI", font=("Arial", 13)).grid(row=1, column=6, sticky="N", padx=10)
        tk.Label(job_view, text="Store", font=("Arial", 13)).grid(row=1, column=7, sticky="N", padx=10)
        tk.Label(job_view, text="Assemble", font=("Arial", 13)).grid(row=1, column=8, sticky="N", padx=10)
        tk.Label(job_view, text="Finish", font=("Arial", 13)).grid(row=1, column=9, sticky="N", padx=10)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    # Create an instance of MESGUI
    my_gui = MESGUI()

    # Run the GUI
    my_gui.run()
