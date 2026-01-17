import asyncio
import websockets
import json
import sys

# Windows-specific fix for Event Loop Policy if needed
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def chat():
    uri = "ws://localhost:8766"
    print(f"🔌 Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri,ping_interval=None, ping_timeout=None) as websocket:
            print("✅ Connected! Type a message.")
            
            while True:
                user_input = input("\nYou: ")
                if user_input.lower() in ["quit", "exit"]: break
                
                # Send JSON
                # CRITICAL: Keep user_id SAME to fix 'Amnesia'
                payload = json.dumps({"user_id": "test_user_1", "input": user_input})
                await websocket.send(payload)
                
                while True:
                    response = await websocket.recv()
                    data = json.loads(response)
                    
                    msg_type = data.get("type")
                    content = data.get("content", "")

                    if msg_type == "PING":
                        print("PING")  # SILENTLY IGNORE PING
                    
                    elif msg_type == "UPDATE":
                        print(f" ℹ️  {content}")
                    
                    elif msg_type == "RESPONSE":
                        print(f"\n🤖 AI: {content}\n")
                    
                    elif msg_type == "DONE":
                        break
                    
                    elif msg_type == "ERROR":
                        print(f"❌ Server Error: {content}")
                        break
                        
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    asyncio.run(chat())