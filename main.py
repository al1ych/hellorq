import csv

# Константы для конвертации
MPH_TO_MPS = 0.44704

def read_csv(file_path):
    """
    Чтение данных из CSV-файла.
    Ожидаемый формат:
    Timestamp,Temperature_F,Humidity_Percent,Pressure_hPa,WindSpeed_mph
    """
    data = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                record = {
                    "Timestamp": row["Timestamp"].strip(),
                    "Temperature_F": float(row["Temperature_F"].strip()),
                    "Humidity_Percent": float(row["Humidity_Percent"].strip()),
                    "Pressure_hPa": float(row["Pressure_hPa"].strip()),
                    "WindSpeed_mph": float(row["WindSpeed_mph"].strip())
                }
                data.append(record)
            except Exception as e:
                print(f"Ошибка при обработке строки {row}: {e}")
    return data

def transform_data(data):
    """
    Применяем преобразования:
    - Конвертация температуры из °F в °C
    - Конвертация скорости ветра из mph в m/s
    """
    for row in data:
        row["Temperature_C"] = (row["Temperature_F"] - 32) * 5.0/9.0
        row["WindSpeed_m/s"] = row["WindSpeed_mph"] * MPH_TO_MPS
    return data

def detect_pressure_anomalies(data):
    """
    Выявление аномальных изменений давления.
    Для каждой записи, начиная со второй, если разница с предыдущим валидным значением превышает 10 hPa,
    запись помечается как аномальная.
    Возвращается список флагов и журнал аномалий.
    """
    anomaly_flags = [False] * len(data)
    anomaly_log = []
    
    last_valid_index = 0  # первый элемент считаем валидным
    
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

    for i, row in enumerate(data):
        row["Corrected_Pressure"] = corrected_pressures[i]
    return data

def filter_low_temperature(data):
    """
    Фильтрация записей, где температура (в °C) ниже 10.
    """
    return [row for row in data if row["Temperature_C"] < 10]

def filter_humidity_anomalies(data):
    """
    Фильтрация записей с аномалиями влажности: ниже 30% или выше 90%.
    """
    return [row for row in data if row["Humidity_Percent"] < 30 or row["Humidity_Percent"] > 90]

def write_csv(file_path, data, fieldnames):
    """
    Запись списка словарей в CSV-файл.
    """
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def main():
    input_file = "sensor_data_550.csv"  # Укажите имя вашего файла
    data = read_csv(input_file)
    if not data:
        print("Нет данных для обработки.")
        return

    # Преобразование данных (конвертация единиц)
    data = transform_data(data)
    
    # Выявление аномалий давления
    anomaly_flags, pressure_anomalies_log = detect_pressure_anomalies(data)
    
    # Корректировка давления с использованием интерполяции
    data = correct_pressure(data, anomaly_flags)
    
    # Фильтрация по низкой температуре и аномальной влажности
    low_temp_data = filter_low_temperature(data)
    humidity_anomalies_data = filter_humidity_anomalies(data)
    
    # Определяем поля для выходных файлов
    processed_fields = [
        "Timestamp", "Temperature_F", "Temperature_C", "Humidity_Percent",
        "Pressure_hPa", "Corrected_Pressure", "WindSpeed_mph", "WindSpeed_m/s"
    ]
    anomaly_fields = ["Timestamp", "Pressure_hPa", "Previous_Pressure", "Difference"]
    
    # Запись файлов с результатами
    write_csv("processed_sensor_data.csv", data, processed_fields)
    write_csv("pressure_anomalies_log.csv", pressure_anomalies_log, anomaly_fields)
    write_csv("low_temperature.csv", low_temp_data, processed_fields)
    write_csv("humidity_anomalies.csv", humidity_anomalies_data, processed_fields)
    
    print("Обработка завершена. Выходные файлы сгенерированы.")

if __name__ == "__main__":
    main()
