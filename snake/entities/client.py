from typing import Union
from uuid import uuid4

from websockets import WebSocketServerProtocol

client_states = [
    {
        "page": "/rooms",
        "current_status": "Looking for a room...",
        "room": {
            "room_created": True,
            "is_owner": False,
        },
        "rooms": {},
        "matches": {},
    }
]


class Client:
    def __init__(self, name: str, socket: WebSocketServerProtocol):
        self.id: str = str(uuid4())
        self.name: str = name
        self.socket: WebSocketServerProtocol = socket
        self.current_room: Union[str, None] = None
        self.state = {
            "page": "/rooms",
            "current_status": "Looking for a room...",
            "room": {
                "room_created": False,
                "is_owner": False,
            },
            "rooms": {},
            "matches": {},
        }

    def get_id(self) -> str:
        return self.id

    def get_name(self) -> str:
        return self.name

    def get_current_room(self) -> str:
        return self.current_room

    def set_current_room(self, room_id: str) -> str:
        self.current_room = room_id

    def set_socket(self, socket: WebSocketServerProtocol):
        self.socket = socket

    def to_dict(self):
        client = {"id": self.id, "name": self.name, "current_room": self.current_room}
        return client

    def change_state(self, **kwargs):
        target_state = kwargs.get("target_state", None)
        page = kwargs.get("page", None)
        payload = kwargs.get("payload", None)
        if page:
            self.state.update({"page": page})
        if target_state and payload:
            self.state.update({target_state: page})
