# filters/write_filter.py
import csv

def write_csv(file_path, data, fieldnames):
    """
    Запись списка словарей в CSV-файл.
    """
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
