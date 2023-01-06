from MES import MES


class Tickable:
    """
    This class acts as a sort of interface, to standardise the tick method. Every class that uses the tick method
    is a child of Tickable
    """
    def tick(self, mes: MES, clock: int):
        """
        Signature for the tick method
        :param mes: Management Execution System
        :param clock: Current Time
        :return: None
        """
        pass

