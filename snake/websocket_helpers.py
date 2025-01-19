import json
from typing import Dict, List, Union

from room import Client
from websockets.server import WebSocketServerProtocol


def broadcast(clients: Union[List[Client], Dict[str, Client]], message: any):
    encoded_message: str = message if isinstance(message, str) else json.dumps(message)
    if isinstance(clients):
        for key in clients:
            client = clients[key]
            client.socket.send(encoded_message)

    if isinstance(clients, list):
        for client in clients:
            client.socket.send(encoded_message)
