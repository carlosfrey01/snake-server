import json
from queue import Queue
from uuid import uuid4

from snake.asyncio_helpers import await_for_event
from snake.entities.client import Client
from snake.event import ClientEvent


class Room:
    def __init__(self, owner: Client, **kwargs: dict):
        super().__init__()
        self.id: str = str(uuid4())
        self.room_queue: Queue = Queue()
        self.clients: dict[str, Client] = {}
        self.owner: Client = owner

        self.match: any = None

        self.title: str = kwargs.get("name", f"{owner.get_name()}'s new room")
        self.max_players: int = kwargs.get("capacity", 10)
        self.min_players: int = kwargs.get("min_players", 2)
        self.match_speed: int = kwargs.get("match_speed", 1)

    def encode(self):
        room = self.to_dict()
        return json.dumps(room)

    def to_dict(self):
        return {
            "name": self.title,
            "max_players": self.max_players,
            "min_players": self.min_players,
            "match_speed": self.match_speed,
            "clients": self.clients,
        }
