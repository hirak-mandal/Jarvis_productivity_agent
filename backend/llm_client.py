import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
api_key=os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("API key not found!!!")
client=Groq(api_key)
model="llama-3.3-70b-versatile"