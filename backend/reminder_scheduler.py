import asyncio
import os
import datetime,timedelta
from apsheduler.schedulers.asyncio import AsyncIOScheduler

def tick():
    print("Tick!The time is:{datetime.now()}")

def main():
    scheduler=AsyncIOSchduler()
    run_time=datetime.now() + timedelta(seconds=5)
    scheduler.add_job(tick,"date",run_date=run_time) #trigger
    scheduler.start() #executar
    print("Press Ctrl+{} to exit".format("Break" if os.name == "nt" else "C"))

    while True:
        await asycio.sleep(1000)

if __name__=="__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt,SystemExit):
        pass