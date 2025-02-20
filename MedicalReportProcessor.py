import json
from PIL import Image, ImageOps
import easyocr
import ollama
import cv2
import numpy as np
import csv

class MedicalReportProcessor:
    def __init__(self, image_path):
        self.image_path = image_path
        self.reader = easyocr.Reader(['ru'])  # Инициализация EasyOCR для английского языка
        self.ollama_model = "mistral"  # Модель Ollama (можно изменить)

    def preprocess_image(self):
        """Преобразует изображение в чёрно-белый формат и подготавливает для OCR."""
        image = Image.open(self.image_path)
        image = ImageOps.grayscale(image)  # Преобразование в чёрно-белый формат
        image = ImageOps.invert(image)  # Инвертирование цветов (если текст светлый на тёмном фоне)
        image.save("processed_image.jpg")  # Сохранение обработанного изображения
        return "processed_image.jpg"


    # def preprocess_image(self):
    #     """Подготавливает изображение для OCR."""
    #     image = Image.open(self.image_path)
    #     image = ImageOps.grayscale(image)
    #
    #     # Увеличение контрастности (можно подкрутить 1.5, 2.0)
    #     image = ImageOps.autocontrast(image)
    #
    #     # Усиление контраста и яркости
    #     from PIL import ImageEnhance
    #     enhancer = ImageEnhance.Contrast(image)
    #     image = enhancer.enhance(2.0)  # Усиление контраста (можно от 1.5 до 3)
    #
    #     # Инвертирование (по необходимости, если текст светлый на темном)
    #     image = ImageOps.invert(image)
    #
    #     # Можно увеличить изображение, но осторожно!
    #     # image = image.resize((image.width * 2, image.height * 2), Image.Resampling.LANCZOS)
    #
    #     image.save("processed_image.jpg")
    #     return "processed_image.jpg"

    # def preprocess_image(self):
    #     """Улучшает изображение для OCR, увеличивает резкость, контраст и устраняет шумы."""
    #     # Открываем изображение и конвертируем его в оттенки серого
    #     image = Image.open(self.image_path)
    #     image = ImageOps.grayscale(image)
    #     image = ImageOps.invert(image)
    #
    #     # Конвертация в массив numpy для работы с OpenCV
    #     img = np.array(image)
    #
    #     # # Увеличиваем или уменьшаем изображение
    #     # height, width = img.shape
    #     # img = cv2.resize(img, (int(width * 2), int(height * 2)), interpolation=cv2.INTER_CUBIC)
    #
    #     # Увеличим контраст с помощью адаптивного выравнивания гистограммы
    #     clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    #     img = clahe.apply(img)
    #
    #     # Увеличение резкости с помощью фильтра повышения резкости
    #     img = cv2.GaussianBlur(img, (0, 0), 3)
    #     img = cv2.addWeighted(img, 1.5, img, -0.5, 0)
    #
    #     # Бинаризация (пороговая обработка)
    #     _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    #
    #     # Устранение мелких шумов
    #     img = cv2.medianBlur(img, 3)
    #
    #     # Сохранение изображения
    #     processed_image_path = "processed_image.jpg"
    #     cv2.imwrite(processed_image_path, img)
    #
    #     return processed_image_path

    def extract_text(self, processed_image_path):
        """Извлекает текст с изображения с помощью EasyOCR."""
        result = self.reader.readtext(processed_image_path)
        extracted_text = " ".join([text[1] for text in result])  # Объединяем весь текст в одну строку
        return extracted_text

    def save_to_json_and_csv(self, data, json_file="output.json", csv_file="output.csv"):
        """Сохраняет данные в JSON и CSV файлы."""

        # Сохранение в JSON
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {json_file}")

        # Сохранение в CSV
        with open(csv_file, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)

            # Заголовки для всех полей
            writer.writerow(["Category", "Test Name", "Value", "Unit", "Normal Range"])

            # Берём только parsed_data, так как extracted_text не нужен в CSV
            parsed_data = data.get("parsed_data", {})

            for category, tests in parsed_data.items():
                for test in tests:
                    if isinstance(test, dict):  # Проверяем, что test - это словарь
                        writer.writerow([
                            category,
                            test.get("Название теста", ""),
                            test.get("Значение", ""),
                            test.get("Единица измерения", ""),
                            test.get("Норма", "")
                        ])
                    else:
                        # Если встретится строка или что-то другое, запишем заглушку, чтобы видеть проблему
                        writer.writerow([category, "НЕИЗВЕСТНО", "НЕИЗВЕСТНО", "НЕИЗВЕСТНО", "НЕИЗВЕСТНО"])

        print(f"Data saved to {csv_file}")

    # def save_to_json(self, data, output_file="output.json"):
    #     """Сохраняет данные в JSON-файл."""
    #     with open(output_file, "w", encoding="utf-8") as f:
    #         json.dump(data, f, ensure_ascii=False, indent=4)
    #     print(f"Data saved to {output_file}")

    def process(self):
        """Основной метод для обработки изображения и извлечения данных."""
        # Шаг 1: Обработка изображения
        processed_image_path = self.preprocess_image()

        # Шаг 2: Извлечение текста
        extracted_text = self.extract_text(processed_image_path)
        print("Extracted Text:", extracted_text)

        # Шаг 3: Обработка текста с помощью Ollama
        parsed_data = self.parse_text_with_ollama(extracted_text)
        print("Parsed Data:", parsed_data)

        # Шаг 4: Сохранение в JSON и CSV
        self.save_to_json_and_csv({"extracted_text": extracted_text, "parsed_data": parsed_data})
