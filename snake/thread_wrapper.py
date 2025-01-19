import time
from threading import Event, Thread


class ThreadWrapper:
    def __init__(self, target, *args, **kwargs):
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.event = Event()
        self.is_running = False

    def start(self):
        args = (self.event,) + self.args
        thread = Thread(target=self.target, args=args, kwargs=self.kwargs)
        self.event.set()
        thread.start()
        self.is_running = True

    def pause(self):
        self.event.clear()
        self.is_running = True

    def resume(self):
        self.event.set()
        self.is_running = True
