from datetime import date


def get_week_type(target_date: date) -> bool:
    """
    Возвращает True, если неделя чётная (вторая), False — если нечётная (первая).
    Отсчёт ведётся от 1 сентября текущего или предыдущего года.
    """
    # Определяем начало учебного года
    if target_date.month >= 9:
        academic_year_start = date(target_date.year, 9, 1)
    else:
        academic_year_start = date(target_date.year - 1, 9, 1)

    # Считаем количество дней от начала учебного года
    days_since_start = (target_date - academic_year_start).days
    if days_since_start < 0:
        # Дата до 1 сентября — относится к предыдущему учебному году
        return get_week_type(date(target_date.year - 1, 12, 31))

    # Номер недели от начала учебного года (начиная с 1)
    week_number = days_since_start // 7 + 1

    # Чётная неделя = вторая
    return week_number % 2 == 0
