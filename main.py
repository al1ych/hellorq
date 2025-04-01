from filters.source_filter import read_csv
from filters.transform_filter import transform_data
from filters.pressure_filter import detect_pressure_anomalies, correct_pressure
from filters.temperature_filter import filter_low_temperature
from filters.humidity_filter import filter_humidity_anomalies
from filters.write_filter import write_csv

def main():
    # Путь к исходному файлу (можно задать через аргументы командной строки, если нужно)
    input_file = "input/sensor_data_550.csv"
    
    # 1) Чтение данных
    data = read_csv(input_file)
    if not data:
        print("Нет данных для обработки.")
        return
    
    # 2) Преобразование данных (конвертация единиц)
    data = transform_data(data)
    
    # 3) Выявление аномалий давления
    anomaly_flags, pressure_anomalies_log = detect_pressure_anomalies(data)
    
    # 4) Корректировка давления с использованием интерполяции
    data = correct_pressure(data, anomaly_flags)
    
    # 5) Фильтрация по низкой температуре и аномальной влажности
    low_temp_data = filter_low_temperature(data)
    humidity_anomalies_data = filter_humidity_anomalies(data)
    
    # Определяем поля для выходных файлов
    processed_fields = [
        "Timestamp", "Temperature_F", "Temperature_C", "Humidity_Percent",
        "Pressure_hPa", "Corrected_Pressure", "WindSpeed_mph", "WindSpeed_m/s"
    ]
    anomaly_fields = ["Timestamp", "Pressure_hPa", "Previous_Pressure", "Difference"]
    
    # Создадим выходную папку, если нужно
    # (Опционально, если вы хотите убедиться, что папка "output" существует)
    import os
    os.makedirs("output", exist_ok=True)
    
    # 6) Запись файлов с результатами
    write_csv("output/processed_sensor_data.csv", data, processed_fields)
    write_csv("output/pressure_anomalies_log.csv", pressure_anomalies_log, anomaly_fields)
    write_csv("output/low_temperature.csv", low_temp_data, processed_fields)
    write_csv("output/humidity_anomalies.csv", humidity_anomalies_data, processed_fields)
    
    print("Обработка завершена. Выходные файлы сгенерированы в папке output/.")

if __name__ == "__main__":
    main()
