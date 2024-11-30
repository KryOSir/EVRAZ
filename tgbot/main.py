import io
import os
from zipfile import ZipFile

from decouple import config
from telebot import TeleBot

from rag import *
import shutil

#from example_of_request import rag, find_relevant_reviews

def build_project_tree(zip_path):
    """
    Создает дерево проекта для заданного ZIP-архива, с полными путями.
    :param zip_path: Путь к ZIP-архиву.
    :return: Строка с деревом проекта.
    """
    try:
        tree = ""
        with ZipFile(zip_path, 'rd') as archive:
            # Получение списка файлов и папок
            all_files = archive.namelist()

            # Сортировка для корректного отображения вложенных структур
            sorted_files = sorted(all_files, key=lambda x: (x.count('/'), x))

            # Формирование дерева с полными путями
            for file in sorted_files:
                tree += f"{file}\n"

        return tree

    except Exception as e:
        return f"Ошибка при построении дерева: {str(e)}"


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


def create_report(report_path, contents):
    """Создаёт текстовый отчёт."""
    with open(report_path, "w", encoding='utf-8') as file:
        file.write(contents)
    return report_path


# Отладочный вывод для проверки импорта config
print(f"Config function: {config}")

# Загрузка конфигурации из .env файла
TOKEN = '7763793823:AAFZvLzyVCIG2lqZ_bLAoUWelExJK6RphgY'

# Создание бота
bot = TeleBot(TOKEN)

def create_report(report_path, contents):
    with open(report_path, "w", encoding='utf-8') as file:
        file.write(contents)
    return report_path

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

        if file_name.endswith('.zip'):
            bot.reply_to(message, "Файл находится в обработке")
            # Дерево проекта
            py_files_tree = build_python_files_tree(file_name)

            # Работа с каждым `.py` файлом
            extracted_dir = f"extracted_{file_name}"
            os.makedirs(extracted_dir, exist_ok=True)
            with ZipFile(file_name, 'r') as archive:
                archive.extractall(extracted_dir)

            all_contents = ""

            rag_response = rag_for_tree(py_files_tree.splitlines())
            content = rag_response.get('choices', [{}])[0].get('message', {}).get('content', 'Нет данных')
            all_contents += f"Структура проекта:\n{py_files_tree} \n{content}\n\n"

            for root, _, files in os.walk(extracted_dir):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = f.read()
                        # Вызов RAG
                        rag_response = rag_for_code(data)
                        # Извлечение контента с мнением
                        content = rag_response.get('choices', [{}])[0].get('message', {}).get('content', 'Нет данных')
                        all_contents += f"Файл: {file_path}\n{content}\n\n"

            # Создание файла отчета
            report_path = create_report(f"report_archive_{file_name}.txt", all_contents)
            r_type = "архив"

            # Удаление распакованных файлов
            shutil.rmtree(extracted_dir)
        else:
            report_path = create_report(f"report_{file_name}.txt", "Обработка файла не реализована.")
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
