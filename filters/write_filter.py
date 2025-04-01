import csv

def write_csv(file_path, data, fieldnames):
    """
    Write a list of dictionaries to a CSV file.
    """
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
