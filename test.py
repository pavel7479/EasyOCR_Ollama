import json
import csv

def read_json(file_path):
    """Читает и выводит данные из JSON-файла."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(json.dumps(data, ensure_ascii=False, indent=4))  # Красивый вывод
    return data


def read_csv(file_path):
    """Читает и выводит данные из CSV-файла."""
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            print(row)


# Укажи свои пути к файлам
json_path = "output.json"
csv_path = "output.csv"

print("Содержимое JSON-файла:")
read_json(json_path)

print("\nСодержимое CSV-файла:")
read_csv(csv_path)
