import json
import time
from typing import Dict, Union

from websockets.server import WebSocketServerProtocol

from snake.asyncio_helpers import await_for_event
from snake.entities.client import Client
from snake.thread_wrapper import ThreadWrapper


class ConnectionsEvents:
    def __init__(self):
        self.event_type = "connections"

    def create_client_event(self, client: Client):
        event = {
            "event_type": "server",
            "action": "create_client_event",
            "payload": client.to_dict(),
        }

        return json.dumps(event)

    def reconnect_event(self, client: Client):
        event = {
            "event_type": "connections",
            "action": "reconnect",
            "payload": client.to_dict(),
        }

        return json.dumps(event)


class Connections(ConnectionsEvents):
    def __init__(self):
        self.connections: Dict[str, Client] = {}
        self.timeout_threads = {}

    def connection_timeout_thread(self, client_id, duration):
        thread = ThreadWrapper(
            target=self.connection_timeout, client_id=client_id, duration=duration
        )
        thread.start()

    def get(self, client_id: str):
        return self.connections.get(client_id, None)

    def connection_timeout(self, **kwargs):
        duration = kwargs.get("duration", None)
        client_id = kwargs.get("client_id", None)
        if duration and client_id:
            while duration:
                print(
                    f"[CONNECTION TIMEOUT]Client of id {client_id} will be removed in {duration} seconds"
                )
                duration -= 1
                time.sleep(1)
            self.connections.pop(client_id)

    def send_message(self, message: any, client_id: str):
        client = self.connections[client_id]
        message_state = {**client.state, **message}
        await_for_event(client.socket.send, json.dumps(message_state))
        print("sent something")

    def broadcast(self, connection_ids: list[str], message: any):
        for id in connection_ids:
            self.send_message(message=message, client_id=id)

    async def create(self, message: dict, socket: WebSocketServerProtocol) -> str:
        payload: dict = message.get("payload", None)
        print(message)
        if payload:
            print("found a payload")
            name = payload.get("name", "No name")
            client = Client(name=name, socket=socket)

            self.connections[client.id] = client

            event = self.create_client_event(client=client)
            await socket.send(event)
            print(f"[CLIENT CREATED]: {id}")
            return client.id

    async def reconnect(self, message: dict, socket: WebSocketServerProtocol):
        payload: Union[dict, None] = message.get("payload", None)

        if payload and (id := payload.get("id", None)):
            if self.connections.get(id, None) is not None:
                client = self.connections[id]
                client.set_socket(socket=socket)
                event = self.reconnect_event(client=client)
                await socket.send(event)

                print(f"[CLIENT REFRESHED]: {id}")
        else:
            print("[COULDN'T REFRESH CLIENT]: no cached user found")


conn = Connections()
