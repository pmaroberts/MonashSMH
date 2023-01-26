from Jeffrey_OPCUA import *
import asyncio
import nest_asyncio

nest_asyncio.apply()


async def get_some_data(op: Opcua):
    data = await op.getValue("ns=11;s=P1f_Ready")
    print(data)


async def set_some_data(op: Opcua):
    await op.setValue("ns=11;s=P1f_Ready", True, ua.VariantType.Boolean)


def main():
    op = Opcua()
    asyncio.run(get_some_data(op))
    asyncio.run(set_some_data(op))
    asyncio.run(get_some_data(op))


if __name__ == '__main__':
    main()
