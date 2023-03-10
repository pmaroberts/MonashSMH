import traceback

from asyncua import Client, ua
import asyncio


class Opcua:
    def __init__(self):
        self.OpcUaHost = 'oct.tpc://172.31.1.236:4840/server/'
        self.opcuaClient = Client(self.OpcUaHost)
        self.nodeDict = {}

    async def setValue(self, node, value, type):
        try:
            await self.opcuaClient.connect()
            if node in self.nodeDict:
                return await self.nodeDict[node].set_value(value, type)
            self.nodeDict[node] = self.opcuaClient.get_node(node)
            print(f'added {node} to dict')
            return await self.nodeDict[node].set_value(value, type)
        except Exception:
            print(f'Error setting value:\n{traceback.print_exc()}')

    async def getValue(self, node):
        try:
            await self.opcuaClient.connect()
            if node in self.nodeDict:
                return await self.nodeDict[node].get_value()
            self.nodeDict[node] = self.opcuaClient.get_node(node)
            print(f'added {node} to dict')
            return await self.nodeDict[node].get_value()
        except Exception:
            print(f'Error getting value:\n{traceback.print_exc()}')
