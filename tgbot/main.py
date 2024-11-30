import os
from zipfile import ZipFile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from telebot import TeleBot
import shutil

# Загрузка токена для бота
TOKEN = 'YOUR_BOT_TOKEN'  # Укажите ваш токен
bot = TeleBot(TOKEN)


def build_python_files_tree(zip_path):
    """
    Создает дерево проекта только для `.py` файлов из ZIP-архива.
    :param zip_path: Путь к ZIP-архиву.
    :return: Строка с деревом проекта, включающим только `.py` файлы.
    """
    try:
        tree_py = ""
        with ZipFile(zip_path, 'r') as archive:
            all_files = archive.namelist()
            py_files = [file for file in all_files if file.endswith('.py')]
            sorted_py_files = sorted(py_files, key=lambda x: (x.count('/'), x))
            for file in sorted_py_files:
                tree_py += f"{file}\n"
        if not py_files:
            tree_py += "Нет `.py` файлов в архиве.\n"
        return tree_py
    except Exception as e:
        return f"Ошибка при построении дерева: {str(e)}"


def create_pdf_report(report_path, contents):
    """
    Создаёт PDF-отчёт.
    :param report_path: Путь для сохранения PDF-файла.
    :param contents: Содержимое отчета.
    :return: Путь к созданному PDF-файлу.
    """
    try:
        pdf_canvas = canvas.Canvas(report_path, pagesize=letter)
        pdf_canvas.setFont("Helvetica", 10)
        pdf_canvas.drawString(30, 750, f"Отчёт сгенерирован: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        y_position = 720
        line_height = 12

        for line in contents.splitlines():
            if y_position < 40:  # Перенос на следующую страницу
                pdf_canvas.showPage()
                pdf_canvas.setFont("Helvetica", 10)
                y_position = 750
            pdf_canvas.drawString(30, y_position, line)
            y_position -= line_height

        pdf_canvas.save()
        return report_path
    except Exception as e:
        return f"Ошибка при создании PDF: {str(e)}"


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

        with open(file_name, 'wb') as new_file:
            new_file.write(downloaded_file)

        if file_name.endswith('.zip'):
            bot.reply_to(message, "Файл находится в обработке")
            py_files_tree = build_python_files_tree(file_name)

            extracted_dir = f"extracted_{file_name}"
            os.makedirs(extracted_dir, exist_ok=True)
            with ZipFile(file_name, 'r') as archive:
                archive.extractall(extracted_dir)

            all_contents = f"Структура проекта:\n{py_files_tree}\n\n"
            for root, _, files in os.walk(extracted_dir):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = f.read()
                        all_contents += f"Файл: {file_path}\nСодержимое:\n{data}\n\n"

            shutil.rmtree(extracted_dir)

            pdf_report_path = f"report_{file_name}.pdf"
            create_pdf_report(pdf_report_path, all_contents)

            if os.path.exists(pdf_report_path):
                with open(pdf_report_path, "rb") as report_file:
                    bot.reply_to(message, "Ваш архив был обработан, результаты прикреплены к сообщению.")
                    bot.send_document(chat_id=message.chat.id, document=report_file)
                os.remove(pdf_report_path)
        else:
            bot.reply_to(message, "Пожалуйста, отправьте ZIP-архив.")

        os.remove(file_name)
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {str(e)}")


@bot.message_handler(func=lambda message: True)
def unknown_command(message):
    bot.reply_to(message, "Я не знаю, что делать с этим. Пожалуйста, отправьте мне ZIP-архив для обработки.")


if __name__ == '__main__':
    print("Bot started")
    bot.infinity_polling()
