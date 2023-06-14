import asyncio
from SummerMES.OPCUAInterface import *


class Monkey:
    def __init__(self):
        self.name = "monkboi"
        self.alive = True

    def kill(self):
        self.alive = False


def gretel_project(monkey: Monkey):
    if monkey.alive:
        monkey.kill()


async def get_some_data(address="ns=11;s=P1d_State"):
    return await OPCUA.get_data(address)


async def set_some_data(value, address="ns=11;s=P1d_State"):
    await OPCUA.set_data(address, value)


def main():
    print(asyncio.get_event_loop().run_until_complete(get_some_data("ns=21;s=R1c_Start")))
    asyncio.get_event_loop().run_until_complete(set_some_data(True, "ns=21;s=R1c_Start"))
    print(asyncio.get_event_loop().run_until_complete(get_some_data("ns=21;s=R1c_Start")))


if __name__ == '__main__':
    main()
