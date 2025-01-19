# from message_queue_handler import message_queue

import json
import logging
from queue import Queue
from threading import Thread
from typing import Dict

from watchpoints import watch

from snake.entities.client import Client
from snake.entities.connections import conn
from snake.entities.room import Room


def kick_client_event(self, actor_name: str, actor_id: str) -> str:
    event = {
        "event_type": self.event_class,
        "action": "kick",
        "payload": {"actor": {"name": actor_name, "id": actor_id}},
    }
    return json.dumps(event)


def client_event(self, **kwargs) -> str:
    event_type = kwargs.get("event_type")
    action = kwargs.get("action")
    payload = kwargs.get("payload")
    event = {
        "event_type": event_type,
        "action": action,
        "payload": payload,
    }
    return json.dumps(event)


class RoomsEvents:
    def __init__(self):
        self.event_type = "rooms"

    def client_subscribe_to_rooms(self):
        event = {
            "name": self.event_type,
            "action": "room_list",
            "payload": self.list_rooms(),
        }
        return event

    def client_fail_create_room_event(self, error_message: str):
        event = {
            "name": self.event_type,
            "action": "fail",
            "payload": {"message": error_message},
        }
        return event

    def client_succeed_create_room_event(self, room: dict):
        event = {
            "name": self.event_type,
            "action": "room_created",
            "transition": "room",
            "payload": {"room": room},
        }
        return event


class Rooms(RoomsEvents):
    def __init__(self, queue: Queue):
        super().__init__()
        self.rooms: Dict[str, Room] = {}
        self.subscribed_clients = {}
        self.queue = queue

        watch(self.rooms, callback=self.broadcast_rooms)
        self.init_consumer()

    def create(self, message: dict, client: Client):
        payload: dict = message.get("payload", None)

        if payload:
            room: dict = payload.get("room", None)
            title = room.get("name", None)

            if title:
                for value in self.rooms.values():
                    if value.title == title:
                        self.client_fail_create_room_event(
                            error_message=f"Room of name {title} already exists"
                        )
                        return
                room = Room(owner=client)
                self.rooms.update({room.id: room})
                event = self.client_succeed_create_room_event(room=room.to_dict())
                conn.send_message(message=event, client_id=client.id)
            else:
                event = self.client_fail_create_room_event(
                    error_message=f"Name was not included in the payload"
                )
                conn.send_message(message=event, client_id=client.id)
        else:
            event = self.client_fail_create_room_event(
                error_message="Payload doesn't exist"
            )
            conn.send_message(message=event)

    def list_rooms(self):
        return [
            {"name": self.rooms[key].title, "capacity": self.rooms[key].max_players}
            for key in self.rooms
        ]

    def join_room(self, client_id: str):
        self.subscribed_clients.append(client_id)

    def subscribe_to_rooms(self, client_id: str):
        self.subscribed_clients[client_id] = conn.get(client_id=client_id)
        event = self.client_subscribe_to_rooms()
        conn.send_message(message=event, client_id=client_id)

    def broadcast_rooms(self, *_):
        event = self.client_subscribe_to_rooms()
        conn.broadcast(connection_ids=self.subscribed_clients.keys(), message=event)

    def handler(self, message: dict):
        action: str = message.get("action", None)
        payload: dict = message.get("payload", None)
        client_id: str = payload.get("client_id", None)

        if client_id:
            client = conn.get(client_id=client_id)
            if action == "create_room":
                self.create(message=message, client=client)
            if action == "subscribe_to_rooms":
                self.subscribe_to_rooms(client_id=client_id)

    def consume_queue(self):
        while True:
            message: dict = self.queue.rooms_queue.get()
            self.handler(message=message)

    def init_consumer(self):
        thread = Thread(target=self.consume_queue)
        thread.start()
