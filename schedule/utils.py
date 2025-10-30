from datetime import date


def get_week_type(target_date: date = None) -> bool:
    """
    Возвращает True, если неделя чётная (вторая), False — если нечётная (первая).
    Логика соответствует Красноярскому ГАУ.
    """
    if target_date is None:
        target_date = date.today()

    year = target_date.year
    new_year = date(year, 1, 1)
    mod_day = new_year.weekday()  # Monday=0, Sunday=6

    day_num = (target_date - new_year).days + 1

    if mod_day < 4:
        week_num = (day_num + mod_day - 1) // 7 + 1
    else:
        week_num = (day_num + mod_day - 1) // 7
        if week_num == 0:
            # Первая неделя относится к предыдущему году
            prev_year = year - 1
            prev_new_year = date(prev_year, 1, 1)
            prev_mod_day = prev_new_year.weekday()
            week_num = 53 if prev_mod_day < 4 else 52

    return week_num % 2 == 0  # True = чётная = вторая неделя
