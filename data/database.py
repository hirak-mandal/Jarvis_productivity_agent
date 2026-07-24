import sqlite3
import json
import asyncio
from data.task_extractor import get_response
from backend.chat import user_data
async def task_extractor(user_data:str):
    response=await get_response(user_data)
    task=json.loads(response)
con=sqlite3.connect("jarvis.db")
cur=con.cursor()
cur.executescript("""
    CREATE TABLE Tasks(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Tasks TEXT,
        Status TEXT
    )""")
cur.execute(f"""INSERT INTO Tasks(Tasks,Status) 
                  Values(?,?)""",({task["task"]},"pending"))
con.commit()
con.close()