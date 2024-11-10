from telebot import TeleBot
from google_sheets import *
from data import *


def send_message_week() -> str:
    """
    Отправляет сообщения с данными за текущую неделю в Telegram чат.

    :return: Строка с подтверждением отправки сообщения.
    """
    # Получим даты текущей недели
    dates_of_week = get_dates_of_current_week()

    # Получим данные за текущую неделю в виде списка строк
    data_list_of_strings = get_data_week(dates_of_week)

    # Отправим сообщения по каждому элементу списка данных
    for _ in data_list_of_strings:
        # Разбиваем сообщение на части, если оно слишком длинное
        message_parts = split_message(_)
        for part in message_parts:
            # Отправляем каждую часть сообщения в чат
            bot.send_message(
                chat_id=MAIN_CHAT_ID,
                text=part,
                parse_mode='Markdown',
                disable_web_page_preview=True,
                timeout=20
            )
    return "Сообщение отправлено!"


if __name__ == "__main__":
    # Инициализируем бота с токеном из data.py
    bot = TeleBot(token=TELEGRAM_BOT_TOKEN)

    # Отправляем сообщение за текущую неделю
    send_message_week()
