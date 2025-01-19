import asyncio


def await_for_event(event, message: any):
    asyncio.run(event(message))
