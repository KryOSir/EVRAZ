import io
import os
from zipfile import ZipFile

from decouple import config
from telebot import TeleBot

# Отладочный вывод для проверки импорта config
print(f"Config function: {config}")

# Загрузка конфигурации из .env файла
TOKEN = '7763793823:AAH-swBh10U8AY6Naqj8rNsSEjXQsQmudsg'

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
            report_path = "report_archive.txt"
            with open(report_path, "w", encoding='utf-8') as report_file:
                report_file.write("Обработка архива не реализована.")
            r_type = "архив"
        else:
            report_path = create_report("report.txt", "Обработка файла не реализована.")
            r_type = "файл"

        # Отправка отчета пользователю
        if os.path.exists(report_path):
            with open(report_path, "rb") as report_file:
                bot.reply_to(message, f"Ваш {r_type} был обработан, результаты прикреплены к сообщению.")
                bot.send_document(chat_id=message.chat.id, document=report_file)
            # Удаление временных файлов
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
