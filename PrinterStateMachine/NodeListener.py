from opcua import Client


def bind_nodes(my_client: Client, node_addresses: list[str], handler: object):
    """
    This method subscribes the handler to the node. Whenever the node changes state,
    the handler will run its datachange_notification method.
    :param my_client: A connected opcua Client object
    :param node_addresses: list of node addresses to subscribe to
    :param handler: A class with a datachange_notification method to handle changes
    :return: None.
    """
    nodes = [my_client.get_node(addr) for addr in node_addresses]
    my_handler = handler
    my_sub = my_client.create_subscription(500, my_handler)
    handle = my_sub.subscribe_data_change(nodes)


class Handler(object):
    def datachange_notification(self, node, val, data):
        pass
