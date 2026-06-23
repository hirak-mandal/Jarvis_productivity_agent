import asyncio
from fastapi import APIRouter,WebSocket,WebSocketDisconnect
from pydantic import BaseModel
from backend.llm_client import get_jarvis_stream
from backend.voice import stream_cartesia_audio
from cartesia import AsyncCartesia
import os
#prefix--> \chat\send or \chat\history
#don't need to add \chat everytime prefix does it for every url
#tag--> creates a section in API documentation for cleaner structure
chat_router=APIRouter(prefix="/chat",tags=["Jarvis Chat"])

#pydantic for data validation
class chatmessage(BaseModel):
    message:str
    client_id:int

#HANDLING DISCONNECTIONS & MULTIPLE CLIENTS
#RESTRICTION --> only for personal use, if want to open for public use it needs cloud(like "Redis")
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket]=[]   #List of active clients

    async def connect(self,websocket: WebSocket):
        await websocket.accept() #two way connection on
        self.active_connections.append(websocket) #Registerin active client

    def disconnect(self,websocket:WebSocket):
        self.active_connections.remove(websocket) #removing inactive client from the list

    async def send_personal_message(self,message:str,websocket:WebSocket):
        await websocket.send_text(message) #1 to 1 messaging

    async def broadcast(self,message:str):
        for connection in self.active_connections:
            await connection.send_text(message) #1 to all messaging 

manager=ConnectionManager()  #instance server

#Websocket---> two way conversation
#standard HTTP --> sent request received response but can't receive another response from backend due to one way connection have to wait for the next request
#Websocket--> real-time streaming(Hybrid capability)
@chat_router.websocket("/stream")
async def handle_chat_system(websocket: WebSocket,client_id:int):
    await manager.connect(websocket) #connection on

    #Initialize Cartesia client here so the websocket stays open during the chat session
    cartesia_api_key = os.getenv("CARTESIA_API_KEY", "PLACEHOLDER_UNTIL_ENV")
    cartesia_client = AsyncCartesia(api_key=cartesia_api_key)

    try:
        while True:
            # 1. Server WAITS for the user to send a prompt
            user_data= await websocket.receive_text()
            #function yields generated tokens to arvis_response
            jarvis_response= await get_jarvis_stream(user_data)

            # Open the streaming pipe to Cartesia
            async with cartesia_client.tts.websocket_connect() as ws:
                ctx = ws.context(
                    model_id="sonic-latest", # Fixed underline string issue
                    voice={"mode": "id", "id": "6ccbfb76-1fc6-48f7-b71d-91ac6298247b"},
                    output_format={"container": "raw", "encoding": "pcm_s16le", "sample_rate": 44100}
                )
                
                # --- TASK 1: Handle Incoming Groq Text -> Send to Frontend & Cartesia ---
                async def text_to_cartesia_task():
                    async for token in jarvis_response:
                        # Send text to client UI instantly
                        await manager.send_personal_message(token, websocket)
                        # Push text to Cartesia voice engine simultaneously
                        await ctx.push(transcript=token, continue_=True)
                    # Close Cartesia context inputs when Groq text runs out
                    await ctx.push(transcript="", continue_=False)

                # --- TASK 2: Handle Incoming Cartesia Audio -> Send straight to Frontend ---
                async def audio_to_frontend_task():
                        async for audio_chunk in stream_cartesia_audio(ctx):
                            # Send raw audio binary chunk to frontend instantly!
                            await websocket.send_bytes(audio_chunk)

                # Fire BOTH tasks concurrently. The audio starts playing while text is still generating!
                await asyncio.gather(
                    text_to_cartesia_task(),
                    audio_to_frontend_task()
                )

            await manager.broadcast(f"Client #{client_id} says: {user_data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")


'''
WEBSOCKET--> HANDLING DISCONNECTION & MULTIPLE CLIENTS
--> Explained by a story:

Imagine you are opening a high-end, real-time Concierge Service inside a bustling hotel.

Your business handles two kinds of clients: some guests just want to talk to their personal Jarvis assistant privately, while other times you need to announce general hotel updates to everyone at once.

To run this smoothly, you hire a chief manager named Leo (this is your ConnectionManager). Leo sets up a desk in the lobby with a physical notebook titled "Active Guests" (self.active_connections).

Let’s look at how the daily operations of this hotel perfectly mirror your architecture.

🛎️ 1. Checking In (The connect method)
A guest named Sarah walks into the hotel lobby. She wants a direct, open line of communication with the concierge team.

       [ Sarah ]  ========================> ( Lobby Desk )
 (Wants to connect)                       | Leo checks his book |
                                          | Adds: "Room 101"    |
The Architecture: Sarah’s browser hits your /stream endpoint.

The Story: Leo (the manager) greets her, performs a security check, and explicitly hands her a special 2-way walkie-talkie (await websocket.accept()).

The Registry: Before Sarah leaves the desk, Leo opens his notebook and writes down her room number: [Room 101] (self.active_connections.append(websocket)). She is now officially registered.

🗣️ 2. The Conversations (send_personal_message vs. broadcast)
Now that Sarah is in her room, she can use her walkie-talkie.

Personal Message (1-to-1)
Sarah presses the button and asks, "Jarvis, what is my schedule today?"
Because Leo's notebook shows Sarah is in Room 101, the AI processes the request and responds directly into Sarah's walkie-talkie. The guests in Room 102 and Room 103 hear absolutely nothing. It is a private, locked channel (send_personal_message).

Broadcast (1-to-All)
Suddenly, the hotel kitchen catches fire. Leo needs to warn everyone instantly. He opens his notebook, looks at the list of registered rooms, and presses a master button that transmits to every single active walkie-talkie simultaneously: "Attention, please exit the building safely!" (broadcast).

🔌 3. Sudden Disconnections (The disconnect method)
This is where things usually get confusing in code, but it makes total sense in the real world.

A guest in Room 102 suddenly goes deep into the hotel basement where there is zero cellular signal. Their walkie-talkie instantly loses power and dies.

    [ Room 102 Walkie-Talkie Dies ]
                 |
                 v
   ( Leo tries to send a Broadcast )
                 |
  [Room 101] -> Works! ✓
  [Room 102] -> CRASH! ✗ (Dead line drops the whole system)
The "Ghost" Problem
If Leo doesn't know the walkie-talkie died, Room 102 stays written in his notebook.
Ten minutes later, Leo tries to broadcast a weather update. He loops through his book:

He radios Room 101. It works perfectly.

He tries to radio Room 102. Because the line is dead, his radio system throws a massive static error (WebSocketDisconnect).

The Crash: If Leo panics and drops his master radio out of shock (an unhandled exception), he never gets to radio Room 103! Room 103 misses the vital update just because Room 102's connection was broken.

How your code solves this:
To prevent this, Leo sets up a safety protocol (try...except).

The absolute second a walkie-talkie loses signal, the system triggers an alert. Leo instantly flips open his notebook, takes out an eraser, and crosses out "Room 102" entirely (manager.disconnect(websocket)).

Now, his notebook is clean. The next time he broadcasts, he completely skips Room 102, keeping the communication lines flowing perfectly for everyone else.

🏢 4. The Multi-Hotel Limit (Scaling Out)
Right now, your hotel is small and cozy. Everything happens in one building, and Leo’s notebook is kept right on his desk in the lobby (this is your Server's RAM).

But your Jarvis service becomes a massive hit! You build a second hotel building right across the street (Server B) and hire a second manager named Max.

   [ Hotel Building A ]                  [ Hotel Building B ]
    Manager: Leo                          Manager: Max
   Notebook: [Room 101, 103]             Notebook: [Room 201, 204]
If a guest in Building A tries to send a "Broadcast to all Jarvis users," Leo looks at his notebook and alerts Room 101 and 103. But because Leo cannot see Max's notebook across the street, the guests in Building B never get the message.

For your personal Jarvis project, having just one building (one server instance) is completely fine! But if you ever want Jarvis to run across multiple distributed servers worldwide, you'll need a "shared master digital notebook" floating in the cloud (like Redis) that both Leo and Max can read at the same time.

'''