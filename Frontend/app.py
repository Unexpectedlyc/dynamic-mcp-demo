from calendar import c

from sympy import im
from utils import connect_to_server
import asyncio


async def run_app():
    print("Running Frontend app...")
    await connect_to_server()


if __name__ == "__main__":
    asyncio.run(run_app())
