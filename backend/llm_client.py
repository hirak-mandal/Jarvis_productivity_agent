import os
import asyncio
from groq import AsyncGroq
from dotenv import load_dotenv

async def main():
    load_dotenv()
    api_key=os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("API key not found!!!")
    client=AsyncGroq(api_key=api_key)
    stream=await client.chat.completions.create(
        messages=[
            "role":"user",
            "content":"You are a helpful assistant."
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.5,
        max_completion_tokens=1024,
        top_p=1,
        stop=None,
        stream=True
    )    

    async for chunk in stream:
        print(chunk.choices[0].delta.content,end=" ")

asyncio.run(main())
