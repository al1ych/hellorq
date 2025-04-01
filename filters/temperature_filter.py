def filter_low_temperature(data):
    """
    Filter records where the temperature (in °C) is below 10.
    """
    return [row for row in data if row["Temperature_C"] < 10]
