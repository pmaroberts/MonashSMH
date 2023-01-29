from Jeffrey_OPCUA import *
import asyncio
from OPCUAInterface import *


async def get_some_data():
    return await OPCUA.get_data("ns=11;s=P1d_State")


async def set_some_data():
    await OPCUA.set_data("ns=11;s=P1d_State", "hi")


def main():
    data = asyncio.run(get_some_data())
    asyncio.run(set_some_data())

    print(f"{data} is cool")


if __name__ == '__main__':
    main()
