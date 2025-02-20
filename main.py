from MedicalReportProcessor import MedicalReportProcessor

# Пример использования
if __name__ == "__main__":
    image_path = "foto/2025-02-01_23-26-13.png"  # Укажите путь к вашему изображению
    processor = MedicalReportProcessor(image_path)
    processor.process()