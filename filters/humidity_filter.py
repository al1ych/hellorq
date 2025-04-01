def filter_humidity_anomalies(data):
    """
    Filter records with humidity anomalies: below 30% or above 90%.
    """
    return [row for row in data if row["Humidity_Percent"] < 30 or row["Humidity_Percent"] > 90]
