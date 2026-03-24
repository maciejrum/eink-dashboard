from datetime import datetime, timedelta


def seconds_until_next_minute(now: datetime) -> float:
    target = now.replace(second=0, microsecond=0)
    if target <= now:
        target += timedelta(minutes=1)
    return max(0.0, (target - now).total_seconds())
