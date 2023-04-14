from database import engine
from tables import schedule
from datetime import date, time, datetime, timedelta

def find_nearest_date(best_date):
    """
    Finding nearest day
    """
    conn = engine.connect()
    select_best_day = schedule.select().where(schedule.c.day==best_date)
    times = conn.execute(select_best_day)
    if times.fetchall() == []:
        select_unique_day = schedule.select().group_by('day')
        days = [date.fromisoformat(day[1]) for day in conn.execute(select_unique_day).fetchall()]
        best_iso = date.fromisoformat(best_date)
        best_date = min(days, key=lambda x: abs(best_iso - x))
        return best_date
    return best_date

def find_nearest_time(best_time, best_date=None):
    """
    Finding nearest day and time
    """
    conn = engine.connect()
    if best_date:
        date = '{}T{}:00'.format(best_date, best_time)
        iso_date = datetime.fromisoformat(date)
        select_best_day = conn.execute(schedule.select().where(schedule.c.day==best_date)).fetchall()
        if select_best_day == []:
            nearest_date = find_nearest_date(best_date)
            select_best_day = conn.execute(schedule.select().where(schedule.c.day==nearest_date)).fetchall()
        start_times = [day[2] for day in select_best_day]
        best_time = min(start_times, key=lambda x: abs(iso_date - x))
        return best_time
    start_times = [day[2] for day in conn.execute(schedule.select()).fetchall()]
    time_iso = time.fromisoformat('{}:00'.format(best_time))
    best_time = min(start_times, key=lambda x: abs(
        timedelta(hours=time_iso.hour, minutes=time_iso.minute) - timedelta(hours=x.hour, minutes=x.minute)))
    return best_time