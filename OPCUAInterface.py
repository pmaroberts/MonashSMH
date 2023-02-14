import logging
import sys

from asyncua import Client


class OPCUA:
    address = 'oct.tpc://172.31.1.236:4840/server/'

    @staticmethod
    async def connector() -> Client:
        logging.disable(sys.maxsize)  # The API logs a lot of stuff to console
        client = Client(OPCUA.address)
        await client.connect()
        return client

    @staticmethod
    async def get_data(node_address: str) -> str:
        try:
            cheat_client = await OPCUA.connector()
            node = cheat_client.get_node(node_address)
            data = await node.get_value()
            return str(data)
        except TimeoutError:
            print("OPCUA Server connection problem")

    @staticmethod
    async def set_data(node_address: str, value):
        try:
            cheat_client = await OPCUA.connector()
            node = cheat_client.get_node(node_address)
            v_type = await node.read_data_type_as_variant_type()
            await node.set_value(value, v_type)
        except TimeoutError:
            print("OPCUA Server connection problem")
