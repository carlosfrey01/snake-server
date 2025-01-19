from queue import Queue


class MessageQueueHandler:
    def __init__(self):
        self.rooms_queue = Queue()
        self.matchs_queue = Queue()
