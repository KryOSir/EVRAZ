import pdfplumber
import re

# Функция для извлечения текста из PDF с использованием pdfplumber
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Функция для удаления лишних переносов строк и пробелов
def clean_text(text):
    # Удаляем лишние переносы строк, заменяя их на пробел
    text = re.sub(r'\n+', ' ', text)  # Заменяет последовательности \n на пробел
    # Убираем пробелы в начале и в конце строки
    text = text.strip()
    # Убираем лишние пробелы между словами (если они есть)
    text = re.sub(r'\s+', ' ', text)
    return text

# Пример использования
pdf_path = './mnt/data/Руководство Python.pdf'
guide_text = extract_text_from_pdf(pdf_path)

# Очищаем текст
cleaned_text = clean_text(guide_text)

# Выводим первые 1000 символов очищенного текста для проверки
print(cleaned_text)
