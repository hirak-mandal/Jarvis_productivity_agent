import os
from groq import AsyncGroq
from backend.system_prompt import system_prompt
from dotenv import load_dotenv

# Load environment and set up client ONCE at startup
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("API key not found!!!")

client = AsyncGroq(api_key=api_key)

async def get_jarvis_stream(user_prompt:str):
    stream=await client.chat.completions.create(
        messages=[
            {
                "role":"system",
                "content":system_prompt
            },
            {
                "role":"user",
                "content":user_prompt
            }
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.4,
        max_completion_tokens=512,
        top_p=1,
        stop=None,
        stream=True
    )    

    async for chunk in stream:
        token=chunk.choices[0].delta.content or ""
        if token:
            yield token
