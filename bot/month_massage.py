from telebot import TeleBot
from google_sheets import *
from data import *


def send_message_month():
    """
    Отправляет сообщения с данными за следующий месяц в Telegram чат.

    :return: None
    """
    # Получим номер и строковое представление следующего месяца
    month = get_next_month()

    # Получим данные за следующий месяц в виде словаря строк
    data_dict_of_strings = get_data_month(month)

    # Отправим сообщения по каждому проекту
    for project in data_dict_of_strings:
        # Разбиваем сообщение на части, если оно слишком длинное
        message_parts = split_message(data_dict_of_strings[project])
        for part in message_parts:
            # Отправляем каждую часть сообщения в чат
            bot.send_message(
                chat_id=MAIN_CHAT_ID,
                text=part,
                parse_mode='Markdown',
                disable_web_page_preview=True,
                timeout=20
            )


if __name__ == "__main__":
    # Инициализируем бота с токеном из data.py
    bot = TeleBot(TELEGRAM_BOT_TOKEN)

    # Отправляем сообщение за следующий месяц
    send_message_month()
