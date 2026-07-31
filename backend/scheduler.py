import datetime as dt
from data.database import get_pending_reminders

#reminders pending to be sent
pending_reminders=get_pending_reminders()
for reminder in pending_reminders:
    reminder_id=reminder[0]
    reminder_task=reminder[1]
    reminder_status=reminder[2]
    reminder_due_date=reminder[3]
    reminder_day=reminder[4]
    reminder_time=reminder[5]

# 1. Map user string inputs to Python's weekday numbers
day_mapping = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6
}

if reminder_day in day_mapping:
    target_weekday = day_mapping[reminder_day.lower()]
    today = dt.date.today()          # Today is Friday, 2026-07-31
    current_weekday = today.weekday() # 4
    
    # 3. Calculate days to add
    days_ahead = target_weekday - current_weekday
    
    # If the target day is today or earlier in the week, shift to next week
    if days_ahead <= 0:
        days_ahead += 7
        
    # 4. Compute target date
    next_date = today + dt.timedelta(days=days_ahead)
    time=dt.datetime.strptime(reminder_time, "%H:%M").time()  # Convert string to time object
    notification_time=dt.datetime.combine(next_date, time)  # Combine date and time into a datetime object
