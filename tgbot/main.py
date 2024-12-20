from zipfile import ZipFile
from telebot import TeleBot
from rag import *
import shutil
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

# Загрузка конфигурации из .env файла
TOKEN = '8178170272:AAHbawFOdZx6kHt8DD9V4sg5gJpFsjK-_3Q'

# Создание бота
bot = TeleBot(TOKEN)


from datetime import datetime

def generate_project_analysis_header(file_name):
    """
    Генерирует заголовок анализа проекта с текущей датой и временем.
    :param file_name: Имя файла (например, `example.zip`).
    :return: Строка формата `Анализ проекта example от 01.01.2024 00:00:00 UTC+3`.
    """
    project_name = file_name.rsplit('.', 1)[0]  # Удаляем расширение
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S UTC+3")
    return f"Анализ проекта {project_name} от {current_time}"


pdfmetrics.registerFont(TTFont("Arial", "ArialRegular.ttf"))  # Укажите путь к файлу шрифта

def split_text_to_fit(text, font_name, font_size, max_width):
    """Разбивает текст на строки, чтобы он помещался в заданную ширину."""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        # Проверяем ширину текущей строки с добавленным словом
        test_line = f"{current_line} {word}".strip()
        line_width = stringWidth(test_line, font_name, font_size)

        if line_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def create_pdf_report(report_path, contents):
    """Создаёт PDF-отчёт с переносом текста, учётом абзацев и выделением жирного текста."""
    pdf = canvas.Canvas(report_path)
    pdfmetrics.registerFont(TTFont("Arial-Bold", "Arial-Bold.ttf"))  # Укажите путь к файлу жирного шрифта
    pdfmetrics.registerFont(TTFont("Arial", "ArialRegular.ttf"))  # Обычный шрифт
    pdf.setFont("Arial", 12)

    x, y = 50, 800  # Начальная позиция
    max_width = 500  # Максимальная ширина текста
    line_spacing = 15  # Межстрочный интервал
    paragraph_spacing = 10  # Дополнительный отступ между абзацами

    font_name_regular = "Arial"
    font_name_bold = "Arial-Bold"
    font_size = 12

    for line in contents.splitlines():
        # Проверяем, начинается ли строка с "Файл:"
        if line.startswith("Файл: "):
            # Устанавливаем жирный шрифт
            pdf.setFont(font_name_bold, font_size)
        else:
            # Используем обычный шрифт
            pdf.setFont(font_name_regular, font_size)

        # Проверяем, является ли строка пустой (признак нового абзаца)
        if not line.strip():
            y -= paragraph_spacing  # Увеличиваем отступ для нового абзаца
            continue

        # Разбиваем строку, если она превышает ширину страницы
        wrapped_lines = split_text_to_fit(line, font_name_regular, font_size, max_width)
        for wrapped_line in wrapped_lines:
            if y < 50:  # Перенос на следующую страницу
                pdf.showPage()
                pdf.setFont("Arial", 12)
                y = 800
            pdf.drawString(x, y, wrapped_line)
            y -= line_spacing

        # Добавляем отступ после абзаца
        y -= paragraph_spacing

    pdf.save()
    return report_path


def read_file_safe(file_path):
    """
    Читает содержимое файла, пытаясь определить корректную кодировку.
    Если ни одна из кодировок не подходит, возвращает сообщение об ошибке.

    :param file_path: Путь к файлу.
    :return: Содержимое файла или сообщение об ошибке.
    """
    encodings = ['utf-8', 'cp1251', 'latin-1']  # Список популярных кодировок
    for encoding in encodings:
        try:
            # Пытаемся прочитать файл с текущей кодировкой
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            # Если возникла ошибка, переходим к следующей кодировке
            continue
        except FileNotFoundError:
            # Обработка случая, если файл не найден
            return f"Ошибка: Файл {file_path} не найден."
        except Exception as e:
            # Любая другая ошибка
            return f"Ошибка при чтении файла {file_path}: {str(e)}"

    # Если ни одна кодировка не подошла
    return f"Ошибка декодирования файла {file_path}. Невозможно прочитать содержимое."


def build_python_files_tree(zip_path):
    """
    Создает дерево проекта только для `.py` файлов из ZIP-архива.
    :param zip_path: Путь к ZIP-архиву.
    :return: Строка с деревом проекта, включающим только `.py` файлы.
    """
    try:
        tree_py = ""
        with ZipFile(zip_path, 'r') as archive:
            # Получение списка всех файлов в архиве
            all_files = archive.namelist()

            # Фильтрация только `.py` файлов
            py_files = [file for file in all_files if file.endswith('.py')]

            # Сортировка для корректного отображения вложенных структур
            sorted_py_files = sorted(py_files, key=lambda x: (x.count('/'), x))

            # Формирование дерева с полными путями для `.py` файлов
            for file in sorted_py_files:
                tree_py += f"{file}\n"

        # Если нет `.py` файлов, добавляем сообщение
        if not py_files:
            tree_py += "Нет `.py` файлов в архиве.\n"

        return tree_py

    except Exception as e:
        return f"Ошибка при построении дерева: {str(e)}"


def extract_zip(zip_path, extract_to="temp_dir"):
    """Извлекает содержимое ZIP-архива в указанную папку."""
    try:
        os.makedirs(extract_to, exist_ok=True)
        with ZipFile(zip_path, 'r') as archive:
            archive.extractall(extract_to)
        return extract_to
    except Exception as e:
        return None


@bot.message_handler(commands=['start'])
def start_message(message):
    welcome_text = (
        "Привет! Я бот для проверки проектов.\n"
        "Отправьте мне файл или архив для обработки."
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(content_types=['document'])
def handle_document(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_name = message.document.file_name

        # Сохранение временного файла
        with open(file_name, 'wb') as new_file:
            new_file.write(downloaded_file)

        bot.reply_to(message, "Файл находится в обработке")

        if file_name.endswith('.zip'):
            # Дерево проекта
            py_files_tree = build_python_files_tree(file_name)

            # Работа с каждым `.py` файлом
            extracted_dir = f"extracted_{file_name}"
            os.makedirs(extracted_dir, exist_ok=True)
            with ZipFile(file_name, 'r') as archive:
                archive.extractall(extracted_dir)

            # Генерация заголовка
            header = generate_project_analysis_header(file_name)

            # Добавляем заголовок к содержимому отчёта
            all_contents = f"{header}\n\n"

            rag_response = rag_for_tree(py_files_tree.splitlines())
            content = rag_response.get('choices', [{}])[0].get('message', {}).get('content', 'Нет данных')
            all_contents += f"Структура проекта:\n{py_files_tree} \n{content}\n\n"

            # Шкала прогресса
            count_of_all_files = sum(1 for _ in py_files_tree.splitlines())
            percent_count_one = count_of_all_files // 3
            percent_count_two = count_of_all_files // 3 * 2
            processed_files = 0

            # Обновление содержания файла для выделения названий жирным
            for root, _, files in os.walk(extracted_dir):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)

                        # Чтение файла с безопасной обработкой кодировок
                        data = read_file_safe(file_path)

                        if "Ошибка декодирования" in data:
                            # Если файл не удалось декодировать, уведомляем пользователя и пропускаем его
                            #bot.reply_to(message, f"Файл {file} содержит недекодируемые символы. Он будет пропущен.")
                            continue

                        # Вызываем обработку RAG и добавляем результат в отчёт
                        rag_response = rag_for_code(data)
                        content = rag_response.get('choices', [{}])[0].get('message', {}).get('content', 'Нет данных')
                        all_contents += f"Файл: {file_path}\n{content}\n\n"

                        processed_files += 1
                        if processed_files == percent_count_one:
                            bot.reply_to(message, "Выполнено 30%")
                        elif processed_files == percent_count_two:
                            bot.reply_to(message, "Выполнено 60%")

            # Создание файла отчета в формате PDF
            report_path = create_pdf_report(f"report_{file_name}.pdf", all_contents)
            r_type = "архив"

            # Удаление распакованных файлов
            shutil.rmtree(extracted_dir)
        else:
            if file_name.endswith('.py'):

                # Генерация заголовка
                header = generate_project_analysis_header(file_name)

                # Добавляем заголовок к содержимому отчёта
                all_content = f"{header}\n\n"

                with open(file_name, 'r', encoding='utf-8') as f:
                    data = f.read()
                rag_response = rag_for_code(data)
                content = rag_response.get('choices', [{}])[0].get('message', {}).get('content', 'Нет данных')
                all_content += f"Файл: {file_name}\n{content}\n\n"
                report_path = create_pdf_report(f"report_{file_name}.pdf", all_content)
                r_type = "файл"
            else:
                report_path = create_pdf_report(f"report_{file_name}.pdf", "Обработка файлов не .py не реализована.")
                r_type = "файл"

        # Отправка отчета пользователю
        if os.path.exists(report_path):
            with open(report_path, "rb") as report_file:
                bot.reply_to(message, f"Ваш {r_type} был обработан, результаты прикреплены к сообщению.")
                bot.send_document(chat_id=message.chat.id, document=report_file)
            os.remove(report_path)
        else:
            bot.reply_to(message, "Произошла ошибка при создании отчета.")

        # Удаление временного файла
        os.remove(file_name)

    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {str(e)}")

@bot.message_handler(func=lambda message: True)
def unknown_command(message):
    bot.reply_to(message, "Я не знаю, что делать с этим. Пожалуйста, отправьте мне файл или архив для обработки.")

if __name__ == '__main__':
    print("Bot started")
    bot.infinity_polling()
