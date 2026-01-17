import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from src.logging.logging import setup_logger

logger = setup_logger(__file__)

# --- Path Setup ---
project_root = os.path.abspath(os.getcwd())
env_path = Path(project_root) / '.env'
load_dotenv(env_path)
src_path = os.path.join(project_root, "src")
sys.path.append(project_root)
sys.path.append(src_path)

# --- Imports ---
from src.api_manager.handler_websocket import client_handler
from websockets.asyncio.server import serve

async def websocket_api():
    print(" WebSocket Server starting on ws://0.0.0.0:8766")
    # 'serve' creates the server object. The 'async with' keeps it running.
    async with serve(client_handler, '0.0.0.0', 8766, ping_interval=None, ping_timeout=None, max_size=None):
        # Keep the server running indefinitely
        await asyncio.get_running_loop().create_future()

async def main():
    try:
        logger.info("Starting the Setup")
        await websocket_api()
    except KeyboardInterrupt:
        logger.info(" Server stopping...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass