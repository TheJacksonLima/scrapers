from datetime import datetime, timezone, timedelta

def my_time_now():
    return datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=-3)))
