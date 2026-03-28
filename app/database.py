import redis.asyncio as redis
import os
from contextlib import asynccontextmanager

VALKEY_URL = os.getenv("VALKEY_URL", "redis://localhost:6379")

@asynccontextmanager
async def get_valkey():
    """
    This is a Context Manager. 
    The code before 'yield' sets up the connection.
    The code after 'yield' (the finally block) cleans it up.
    """
    client = redis.from_url(VALKEY_URL, decode_responses=True)
    try:
        yield client
    finally:
        # This is where the magic happens!
        # It closes the connection even if an error occurs.
        await client.close()