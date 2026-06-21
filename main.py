import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.chat import chat_router

#The central command center of backend server
app=FastAPI(
    title="Jarvis_productivity_agent",
    description="A productivity agent that helps you manage your tasks and schedule.",
    version="1.0.0"
)

#security configurations: Cros-origin resource sharing
#Frontend--> one path & Backend--> one path
#can't talk due to Browsers same-origin policy
#but middleware allows to talk to different origin websites
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #allow all websites to talk
    allow_credentials=True, #allowing all cookies and sequrity check
    allow_methods=["*"], #allow GET,POST,DELETE,UPDATE methods
    allow_headers=["*"] #allow all headers
)

#sub-commands(routers) into the central hub
app.include_router(chat_router)

#Root health check endpoint
@app.get("/")
def home():
    return {"status":"online","Agent":"Jarvis"}

if __name__=="__main__":
    #run the ASGI server locally on port 8000
    uvicorn.run("main.py:app",host="127.0.0.1",port=8000,reload=True)