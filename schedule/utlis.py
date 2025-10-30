from datetime import datetime

def y2k(number: int) -> int:
    return number + 1900 if number < 1000 else number

def get_week_type(today: datetime) -> bool:
    year, month, day = y2k(today.year), today.month, today.day

    when = datetime(year, month, day)
    new_year = datetime(year, 1, 1)
    mod_day = new_year.weekday()
    if mod_day == 0:
        mod_day = 6
    else:
        mod_day -= 1

    day_num = (when - new_year).days + 1

    if mod_day < 4:
        week_num = (day_num + mod_day - 1) // 7 + 1
    else:
        week_num = (day_num + mod_day - 1) // 7

        if week_num == 0:
            year -= 1
            prev_new_year = datetime(year, 1, 1)
            prev_mod_day = prev_new_year.weekday()

            if prev_mod_day == 0:
                prev_mod_day = 6
            else:
                prev_mod_day -= 1

            if prev_mod_day < 4:
                week_num = 53
            else:
                week_num = 52
    return week_num % 2 == 0