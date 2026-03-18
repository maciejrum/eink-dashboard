from datetime import datetime


def seconds_until_next_half_hour(now: datetime) -> float:
    minute = now.minute
    if minute < 30:
        target_minute = 30
        target_hour = now.hour
        target_date = now.date()
    else:
        target_minute = 0
        target_hour = (now.hour + 1) % 24
        target_date = now.date()
        if target_hour == 0:
            target_date = now.date().fromordinal(now.date().toordinal() + 1)

    target = datetime(
        year=target_date.year,
        month=target_date.month,
        day=target_date.day,
        hour=target_hour,
        minute=target_minute,
        second=0,
    )
    return max(0.0, (target - now).total_seconds())

