def filter_low_temperature(data):
    """
    Фильтрация записей, где температура (в °C) ниже 10.
    """
    return [row for row in data if row["Temperature_C"] < 10]
