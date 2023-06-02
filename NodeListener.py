from test_state_machine import PrinterStateMachine


class Handler(object):
    def __init__(self, state_machine: PrinterStateMachine):
        self.state_machine = state_machine

    def datachange_notification(self, node, val, data):
        pass


class StartHandler(Handler):
    def datachange_notification(self, node, val, data):
        # print(f"{val} from starthandler")
        if val:
            self.state_machine.heat()


class BedTempHandler(Handler):
    def datachange_notification(self, node, val, data):
        self.state_machine.set_bed_temp(val)
        # print(f'\t{val} from bedtemp')


class NozTempHandler(Handler):
    def datachange_notification(self, node, val, data):
        self.state_machine.set_noz_temp(val)
        # print(f'\t{val} from noztemp')


class EndHandler(Handler):
    def datachange_notification(self, node, val, data):
        if val:
            self.state_machine.print_done()


class PartRemovedHandler(Handler):
    def datachange_notification(self, node, val, data):
        if val:
            self.state_machine.part_removed()

