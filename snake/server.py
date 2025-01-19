import asyncio
import json
import logging
from typing import Generic, TypeVar

import websockets
from pydantic import BaseModel, Field
from websockets.server import WebSocketServerProtocol

from snake.asyncio_helpers import await_for_event
from snake.entities import queue
from snake.entities.connections import conn


class Server:
    def __init__(self):
        super().__init__()

    async def handle_connection(self, websocket: WebSocketServerProtocol):
        data = await websocket.recv()
        first_message: dict = json.loads(data)
        client_id = None
        await conn.reconnect(message=first_message, socket=websocket)
        try:
            async for message in websocket:
                data = json.loads(message)
                if data["name"] == "auth":
                    client_id = await conn.create(message=data, socket=websocket)
                    logging.warning("[WARNING][auth] user has been authenticated")
                if client_id:
                    data["payload"].update({"client_id": client_id})
                    if data["name"] == "rooms":
                        queue.rooms_queue.put(data)
                        logging.warning("[WARNING][rooms] inserting in queue")
                    if data["name"] == "matches":
                        queue.matchs_queue.put(data)
                        logging.warning("[WARNING][matches] inserting in queue")
        except websockets.exceptions.ConnectionClosed as e:
            conn.connection_timeout_thread(client_id=client_id, duration=5)
            print("Connection closed:", e)

    async def main(self):
        async with websockets.serve(self.handle_connection, "localhost", 6789):
            print("WebSocket server is running on ws://localhost:6789")
            await asyncio.Future()


if __name__ == "__main__":
    server = Server()
    asyncio.run(server.main())
