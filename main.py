import csv

# Константы для конвертации
MPH_TO_MPS = 0.44704

def read_csv(file_path):
    """
    Чтение данных из CSV-файла.
    Ожидаемый формат: 
    Timestamp,Temperature(F),Humidity(%),Pressure (hPa), Wind Speed (mph)
    """
    data = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Убираем лишние пробелы и преобразуем числовые поля
            try:
                record = {
                    "Timestamp": row["Timestamp"].strip(),
                    "Temperature(F)": float(row["Temperature(F)"].strip()),
                    "Humidity": float(row["Humidity(%)"].strip()),
                    "Pressure": float(row["Pressure (hPa)"].strip()),
                    "Wind Speed (mph)": float(row[" Wind Speed (mph)"].strip() if " Wind Speed (mph)" in row else row["Wind Speed (mph)"].strip())
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
        row["Temperature(C)"] = (row["Temperature(F)"] - 32) * 5.0/9.0
        row["Wind Speed (m/s)"] = row["Wind Speed (mph)"] * MPH_TO_MPS
    return data

def detect_pressure_anomalies(data):
    """
    Выявление аномальных изменений давления.
    Для каждой записи, начиная со второй, если разница по сравнению с предыдущим валидным значением превышает 10 hPa,
    то запись помечается как аномальная.
    Возвращается список флагов для каждой записи и журнал аномалий.
    """
    anomaly_flags = [False] * len(data)
    anomaly_log = []
    
    # Первый элемент считаем валидным
    last_valid_index = 0
    
    for i in range(1, len(data)):
        current_pressure = data[i]["Pressure"]
        last_valid_pressure = data[last_valid_index]["Pressure"]
        if abs(current_pressure - last_valid_pressure) > 10:
            anomaly_flags[i] = True
            anomaly_log.append({
                "Timestamp": data[i]["Timestamp"],
                "Pressure": current_pressure,
                "Previous Pressure": last_valid_pressure,
                "Difference": abs(current_pressure - last_valid_pressure)
            })
        else:
            last_valid_index = i  # обновляем индекс последнего валидного значения
    return anomaly_flags, anomaly_log

def correct_pressure(data, anomaly_flags):
    """
    Корректировка аномальных значений давления с помощью линейной интерполяции.
    Для каждого непрерывного блока аномалий определяется граница слева (последнее валидное значение)
    и справа (следующее валидное значение). Если справа нет валидного значения, используется последнее валидное.
    """
    # Создаём копию оригинальных значений давления
    corrected_pressures = [row["Pressure"] for row in data]
    n = len(data)
    i = 0
    while i < n:
        if not anomaly_flags[i]:
            i += 1
            continue
        # Начало блока аномалий
        start_index = i - 1 if i > 0 else i
        j = i
        while j < n and anomaly_flags[j]:
            j += 1
        # j — индекс первого валидного значения после блока или n, если блок до конца
        start_value = corrected_pressures[start_index]
        if j < n:
            end_value = corrected_pressures[j]
            # Интерполяция для каждого индекса в блоке аномалий
            for k in range(i, j):
                fraction = (k - start_index) / (j - start_index)
                corrected_pressures[k] = start_value + fraction * (end_value - start_value)
        else:
            # Если валидного значения справа нет, используем последнее валидное значение
            for k in range(i, j):
                corrected_pressures[k] = start_value
        i = j

    # Добавляем скорректированное значение в каждую запись
    for i, row in enumerate(data):
        row["Corrected Pressure"] = corrected_pressures[i]
    return data

def filter_low_temperature(data):
    """
    Отбор записей с температурой ниже 10°C.
    """
    return [row for row in data if row["Temperature(C)"] < 10]

def filter_humidity_anomalies(data):
    """
    Отбор записей с аномалией влажности: ниже 30% или выше 90%.
    """
    return [row for row in data if (row["Humidity"] < 30 or row["Humidity"] > 90)]

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
    input_file = "sensor_data_550.csv"  # замените на актуальное имя файла, если требуется
    data = read_csv(input_file)
    if not data:
        print("Нет данных для обработки.")
        return

    # Этап преобразований
    data = transform_data(data)
    
    # Обнаружение аномалий давления
    anomaly_flags, pressure_anomalies_log = detect_pressure_anomalies(data)
    
    # Корректировка давления
    data = correct_pressure(data, anomaly_flags)
    
    # Формирование выборок для низкой температуры и аномалий влажности
    low_temp_data = filter_low_temperature(data)
    humidity_anomalies_data = filter_humidity_anomalies(data)
    
    # Определяем список полей для каждого выходного файла
    processed_fields = ["Timestamp", "Temperature(F)", "Temperature(C)", "Humidity", "Pressure", "Corrected Pressure", "Wind Speed (mph)", "Wind Speed (m/s)"]
    anomaly_fields = ["Timestamp", "Pressure", "Previous Pressure", "Difference"]
    
    # Запись выходных файлов
    write_csv("processed_sensor_data.csv", data, processed_fields)
    write_csv("pressure_anomalies_log.csv", pressure_anomalies_log, anomaly_fields)
    write_csv("low_temperature.csv", low_temp_data, processed_fields)
    write_csv("humidity_anomalies.csv", humidity_anomalies_data, processed_fields)
    
    print("Обработка завершена. Выходные файлы сгенерированы.")

if __name__ == "__main__":
    main()
