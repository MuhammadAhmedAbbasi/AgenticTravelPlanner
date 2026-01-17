import asyncio
import os
import sys
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

project_root = os.path.abspath(os.getcwd())
env_path = Path(project_root) / '.env'
load_dotenv(env_path)
src_path = os.path.join(project_root, "src")
sys.path.append(project_root)
sys.path.append(src_path)

from src.model_service.model_service import TravelAutomationSystem
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from src.api_manager.connection_manager import ConnectionManager


# --- 4. INITIALIZE APP & SYSTEM ---
app = FastAPI()
manager = ConnectionManager()

print("🚀 Initializing AI Travel System...")
trip_system = TravelAutomationSystem() # initialized ONCE
print("✅ System Ready.")

async def heartbeat(user_id):
    try:
        while True:
            await asyncio.sleep(10)
            await manager.send_personal_message("PING", user_id)
            print("HeartBeat Sent")

    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"💔 Heartbeat stopped for {user_id}: {e}")

# --- 5. WEBSOCKET HANDLER ---
@app.websocket("/ws/{user_id}")
async def websocket_handler(websocket: WebSocket, user_id: str):
    """
    This function runs INDEPENDENTLY for every single user who connects.
    """
    # A. Accept the connection
    await manager.connect(websocket, user_id)
    heartbeat_task = asyncio.create_task(heartbeat(user_id))
    # Get the main event loop to schedule updates from the background thread
    loop = asyncio.get_running_loop()
    
    try:
        # B. The Infinite Loop (Keep connection open)
        while True:
            # 1. WAIT for message
            user_text = await websocket.receive_text()
            print(f"📩 Received from {user_id}: {user_text}")

            # Define the callback function that runs in the background thread
            def status_callback(message: str):
                # Schedule the async send_personal_message on the main event loop
                asyncio.run_coroutine_threadsafe(
                    manager.send_personal_message(f"UPDATE: {message}", user_id),
                    loop
                )

            # 2. PROCESS with AI
            ai_response = await asyncio.to_thread(
                trip_system.run_trip_planner, 
                user_id=user_id, 
                user_input=user_text,
                on_update=status_callback  # Pass the callback here
            )

            # 3. SEND Reply
            await manager.send_personal_message(ai_response, user_id)
            
            # 4. SEND DONE SIGNAL (So client knows to stop listening)
            await manager.send_personal_message("[DONE]", user_id)
            
            print(f"fw Sent to {user_id}: Response generated.")

    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"⚠️ Error for user {user_id}: {e}")
        manager.disconnect(user_id)
    finally:
        # 2. CRITICAL: KILL THE HEARTBEAT WHEN CONNECTION DIES
        heartbeat_task.cancel()

# --- 6. RUNNER ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)