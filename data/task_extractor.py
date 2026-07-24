#NO natural Output to extract task or reminder from user prompt
#Natural Output --> Cartesia reads
#Sturctured Output --> Extractor extracts task or reminder from user prompt
import os
from groq import AsyncGroq
from dotenv import load_dotenv

# Load environment and set up client ONCE at startup
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("API key not found!!!")

client = AsyncGroq(api_key=api_key)

async def get_response(user_prompt:str):
    response=await client.chat.completions.create(
        messages=[
            {
                "role":"system",
                "content":"""Role: You are Jarvis, a hyper-focused, ultra-productive desktop AI agent.
Objective:make to-do, send notifications,send monthly report in Gmail.
TIME RULES:
- Convert all times to 24-hour format (HH:MM).
- Preserve relative dates exactly as mentioned by the user.
- Do NOT calculate calendar dates.
- Do NOT explain your output.
- Return ONLY valid JSON.

STYLE:
1. highly concise—ideally 1 to 3 sentences.
2. Speak directly and professionally.

OUTPUT:
- Return structured answer.
EXAMPLE:
1. USER PROMPT:I need to study AI tomorrow.
YOUR OUTPUT:(FOR TASK)
{
  "intent":"create_task",
  "task":"study AI",
  "due_date":"tomorrow"
}

2. USER PROMPT:Remind me to call John at 3 PM on Friday.
YOUR OUTPUT:(FOR REMINDER)
{
  "intent": "create_reminder",
  "task": "call John",
  "reminder_day": "Friday",
  "reminder_time": "15:00"
}"""
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
    )    

    return response.choices[0].message.content
