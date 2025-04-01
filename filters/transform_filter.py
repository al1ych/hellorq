MPH_TO_MPS = 0.44704

def transform_data(data):
    """
    Apply convertations:
    - Convert temperature from F to °C
    - Convert wind speed from mph to m/s
    """
    for row in data:
        row["Temperature_C"] = (row["Temperature_F"] - 32) * 5.0/9.0
        row["WindSpeed_m/s"] = row["WindSpeed_mph"] * MPH_TO_MPS
    return data
