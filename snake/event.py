import json
from typing import Union
from uuid import uuid4

from websockets.server import WebSocketServerProtocol


class ClientEvent:
    def __init__(self, event_type: any, payload: any, action: any):
        self.event_type = event_type
        self.action = action
        self.payload = payload


# class Events:
#     def __init__(self):
#         self.event_queue = Queue(maxsize=50)
#         self.game_thread: ThreadWrapper = None

#     def consume_event_queue(self):
#         while True:
#             event: dict = self.event_queue.get()
#             name = event.get("name", None)
#             payload = event.get("payload", None)
#             if name:
#                 if name == "start_game":
#                     self.start()
#                     for client in self.clients:
#                         event = json.dumps({"name": name})
#                         asyncio.run(client.send(event))
#                     print("started the game")
#                 if name == "pause_game":
#                     self.game_thread.pause()
#                     for client in self.clients:
#                         event = json.dumps({"name": name})
#                         asyncio.run(client.send(event))
#                 if name == "resume_game":
#                     self.game_thread.resume()
#                     for client in self.clients:
#                         event = json.dumps({"name": name})
#                         asyncio.run(client.send(event))
#                 if name == "key_read":
#                     key = event.get("key", None)
#                     server_key = input_mapping[key]
#                     self.input_queue.put(server_key)
#                     print(server_key)

#     def init_consume_event_queue(self):
#         thread = Thread(target=self.consume_event_queue)
#         thread.start()

#     def add_to_event_queue(self, event):
#         self.event_queue.put(event)

#     def start(self):
#         self.game_thread = ThreadWrapper(target=self.game_start)
#         self.game_thread.start()

#     def pause_game(self):
#         pass

#     def run_game(self):
#         self.start()

#     def init_consume_event_queue(self):
#         thread = Thread(target=self.consume_event_queue)
#         thread.start()
