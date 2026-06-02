from fastapi import APIRouter,WebSocket,WebSocketDisconnect
from pydantic import BaseModel
#prefix--> \chat\send or \chat\history
#don't need to add \chat everytime prefix does it for every url
#tag--> creates a section in API documentation for cleaner structure
chat_router=APIRouter(prefix="/chat",tag=["Jarvis Chat"])

#pydantic for data validation
class chatmessage(BaseModel):
    message:str
    
#Websocket---> two way conversation
#standard HTTP --> sent request received response but can't receive another response from backend due to one way connection have to wait for the next request
#Websocket--> real-time streaming(Hybrid capability)
@chat_router.websocket("/stream")
async def handle_chat_system(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # recieve real-time text from user
            data= await websocket.receive_text()
            #send response back token by token 
            await websocket.send_text(f"Jarvis streaming:{data}")
    except WebSocketDisconnect:
        return "client disconnected from chat steam"