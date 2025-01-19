import asyncio

from snake.server import Server


def start():
    server = Server()
    asyncio.run(server.main())
