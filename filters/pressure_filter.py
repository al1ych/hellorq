# filters/pressure_filter.py

def detect_pressure_anomalies(data):
    """
    Выявление аномальных изменений давления.
    Для каждой записи, начиная со второй, если разница с предыдущим валидным значением превышает 10 hPa,
    запись помечается как аномальная.
    Возвращается список флагов и журнал аномалий.
    """
    anomaly_flags = [False] * len(data)
    anomaly_log = []
    
    last_valid_index = 0 
    
    for i in range(1, len(data)):
        current_pressure = data[i]["Pressure_hPa"]
        last_valid_pressure = data[last_valid_index]["Pressure_hPa"]
        if abs(current_pressure - last_valid_pressure) > 10:
            anomaly_flags[i] = True
            anomaly_log.append({
                "Timestamp": data[i]["Timestamp"],
                "Pressure_hPa": current_pressure,
                "Previous_Pressure": last_valid_pressure,
                "Difference": abs(current_pressure - last_valid_pressure)
            })
        else:
            last_valid_index = i
    return anomaly_flags, anomaly_log

def correct_pressure(data, anomaly_flags):
    """
    Корректировка аномальных значений давления с помощью линейной интерполяции.
    """
    corrected_pressures = [row["Pressure_hPa"] for row in data]
    n = len(data)
    i = 0
    while i < n:
        if not anomaly_flags[i]:
            i += 1
            continue
        start_index = i - 1 if i > 0 else i
        j = i
        while j < n and anomaly_flags[j]:
            j += 1
        start_value = corrected_pressures[start_index]
        if j < n:
            end_value = corrected_pressures[j]
            for k in range(i, j):
                fraction = (k - start_index) / (j - start_index)
                corrected_pressures[k] = start_value + fraction * (end_value - start_value)
        else:
            for k in range(i, j):
                corrected_pressures[k] = start_value
        i = j

    for idx, row in enumerate(data):
        row["Corrected_Pressure"] = corrected_pressures[idx]
    return data
