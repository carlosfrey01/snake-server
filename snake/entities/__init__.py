from .message_queue_handler import MessageQueueHandler
from .rooms import Rooms

queue = MessageQueueHandler()
rooms = Rooms(queue)
