import csv

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
