import json
import asyncio
import websockets
from src.model_service.model_service import TravelAutomationSystem

# Initialize system once
print("🚀 Initializing AI Travel System...")
trip_system = TravelAutomationSystem()
print("✅ System Ready.")

HEARTBEAT_INTERVAL = 5

async def client_handler(websocket):
    client_id = id(websocket)
    loop = asyncio.get_running_loop()
    
    # 🔒 Create a Lock for this specific connection
    # This ensures Heartbeat and AI don't write at the same time
    socket_lock = asyncio.Lock()
    
    # --- Helper to Send Safely ---
    async def safe_send(payload: dict):
        """Thread-safe helper to send JSON data"""
        async with socket_lock:
            try:
                await websocket.send(json.dumps(payload))
            except websockets.exceptions.ConnectionClosed:
                pass # Connection already dead
            except Exception as e:
                print(f"⚠️ Send Error: {e}")

    # --- Heartbeat Task ---
    async def send_heartbeat():
        while True:
            try:
                await asyncio.sleep(HEARTBEAT_INTERVAL)
                await safe_send({"type": "PING"})
            except asyncio.CancelledError:
                break
            except Exception:
                break

    print(f"🔌 New connection: {websocket.remote_address}")
    heartbeat_task = asyncio.create_task(send_heartbeat())

    try:
        async for data in websocket:
            try:
                message = json.loads(data)
                user_input = message.get("input")
                # Use a consistent ID so the AI remembers context
                user_id = message.get("user_id", "default_user") 

                print(f"📩 Request from {user_id}: {user_input}")

                # --- Callback for AI Updates ---
                def status_callback(msg_text: str):
                    # Schedule the safe_send on the main loop
                    asyncio.run_coroutine_threadsafe(
                        safe_send({"type": "UPDATE", "content": msg_text}), 
                        loop
                    )

                # --- Run AI (Non-Blocking) ---
                ai_response = await asyncio.to_thread(
                    trip_system.run_trip_planner,
                    user_id=user_id,
                    user_input=user_input,
                    on_update=status_callback
                )

                # Send Final Response
                await safe_send({"type": "RESPONSE", "content": ai_response})
                await safe_send({"type": "DONE"})

            except json.JSONDecodeError:
                await safe_send({"type": "ERROR", "content": "Invalid JSON"})
            except Exception as e:
                print(f"⚠️ Processing Error: {e}")
                await safe_send({"type": "ERROR", "content": str(e)})

    except websockets.exceptions.ConnectionClosed:
        print(f"🔌 Connection closed: {websocket.remote_address}")
    except Exception as e:
        print(f"⚠️ Critical Error: {str(e)}")
    finally:
        heartbeat_task.cancel()
        print(f"🛑 Handler finished for {websocket.remote_address}")