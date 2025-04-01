def filter_humidity_anomalies(data):
    """
    Фильтрация записей с аномалиями влажности: ниже 30% или выше 90%.
    """
    return [row for row in data if row["Humidity_Percent"] < 30 or row["Humidity_Percent"] > 90]
