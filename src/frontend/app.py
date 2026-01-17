import streamlit as st
import asyncio
import websockets
import json
import uuid

# --- Page Config ---
st.set_page_config(page_title="AI Travel Planner", page_icon="✈️", layout="wide")
st.title("✈️ AI Travel Planner")

# --- 1. Session State Setup ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "Hello! Where would you like to travel?"})

if "user_id" not in st.session_state:
    st.session_state.user_id = f"user_{uuid.uuid4().hex[:8]}"

# --- 2. Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 3. The Logic Function ---
async def chat_logic(user_prompt):
    uri = "ws://localhost:8766"
    
    # Placeholder for the AI's "Thinking" status or temporary messages
    assistant_message_placeholder = st.empty()
    
    try:
        async with websockets.connect(uri, ping_interval=None, ping_timeout=None) as websocket:
            
            # A. Send User Input
            payload = json.dumps({
                "user_id": st.session_state.user_id,
                "input": user_prompt
            })
            await websocket.send(payload)

            # B. Listen for Responses
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                
                msg_type = data.get("type")
                content = data.get("content", "")

                # --- IGNORE PINGS ---
                if msg_type == "PING":
                    continue

                # --- THE MAGIC SWITCH ---
                # This checks for the signal in ANY message type (UPDATE or RESPONSE)
                if "All_Details_Fetched" in content:
                    
                    # Clear the "thinking" text if it exists
                    assistant_message_placeholder.empty()
                    
                    # C. START PLANNING PHASE
                    with st.status("🗺️ Planning your trip...", expanded=True) as status:
                        
                        # Inner Loop: We stay here until the final itinerary arrives
                        while True:
                            new_msg = await websocket.recv()
                            new_data = json.loads(new_msg)
                            new_type = new_data.get("type")
                            new_content = new_data.get("content", "")

                            if new_type == "PING":
                                continue
                            
                            # 1. Show Logs (Searching, Booking, etc.)
                            elif new_type == "UPDATE":
                                # Filter out the switch signal if it repeats
                                if "All_Details_Fetched" not in new_content:
                                    st.write(f"⚙️ {new_content}")
                            
                            # 2. Show Final Result
                            elif new_type == "RESPONSE":
                                status.update(label="✅ Trip Planned!", state="complete", expanded=False)
                                
                                st.markdown("---")
                                st.markdown("### 🎉 Your Trip Itinerary")
                                st.markdown(new_content)
                                
                                # Save result to history
                                st.session_state.messages.append({"role": "assistant", "content": new_content})
                                return # DONE
                                
                            elif new_type == "ERROR":
                                st.error(new_content)
                                return

                # --- STANDARD CHATBOT MODE ---
                # Handle updates like "Analyzing request..." so the user knows it's working
                elif msg_type == "UPDATE":
                    with assistant_message_placeholder.container():
                        st.info(f"🤖 {content}")

                # Handle normal questions from the AI
                elif msg_type == "RESPONSE":
                    # Clear the "Analyzing" info before showing the question
                    assistant_message_placeholder.empty()
                    
                    with st.chat_message("assistant"):
                        st.markdown(content)
                    
                    st.session_state.messages.append({"role": "assistant", "content": content})
                    return # Hand control back to user to type answer

                elif msg_type == "ERROR":
                    st.error(f"Error: {content}")
                    return

    except Exception as e:
        st.error(f"Connection Error: {e}")

# --- 4. Handle User Input ---
if prompt := st.chat_input("Type your answer here..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    asyncio.run(chat_logic(prompt))