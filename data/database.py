import sqlite3
import json
from data.task_extractor import get_response


async def save_task_remainder(data: dict):
    con = sqlite3.connect("jarvis.db")
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Tasks(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Task TEXT,
    Status TEXT,
    Due_Date TEXT,
    Reminder_Day TEXT,
    Reminder_Time TEXT
)
    """)

    cur.execute(
        "INSERT INTO Tasks(Task, Status, reminder_day, reminder_time) VALUES (?, ?, ?, ?)",
        (data["task"], "pending", data.get("reminder_day"), data.get("reminder_time"))
    )

    con.commit()
    con.close()

async def process_user_input(user_data:str):
    response= await get_response(user_data)
    data= json.loads(response)
    intent=data.get("intent")

    if intent in ["create_task","create_reminder"]:
        await save_task_remainder(data)