import json
import gspread
import requests
import datetime
import re

from google.oauth2.service_account import Credentials
from data import *


def get_data_week(week_dates: set) -> list[str]:
    """
    Получает данные за указанную неделю и формирует сообщения для каждого проекта.

    :param week_dates: Множество дат недели в формате 'дд.мм'
    :return: Список строк, содержащих сообщения о проектах и их активности на указанной неделе
    """
    get_creds()
    # Путь к файлу credentials.json
    creds_file = 'credentials.json'

    # Авторизация и подключение к Google Sheets
    creds = Credentials.from_service_account_file(
        creds_file,
        scopes=['https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive']
    )
    client = gspread.authorize(creds)

    # Открой таблицу по ее URL или ID
    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/19zTcjsbXsutwB_fMEJMD1k8611ZdBS1B5nj0qCT-nZ0/edit?gid=0#gid=0'
    spreadsheet = client.open_by_url(spreadsheet_url)
    # Явно выбираем лист по имени (замените 'Рабочая лента' на нужное имя)
    sheet = spreadsheet.worksheet('Рабочая лента')
    # Получаем все значения из нужных столбцов
    table = sheet.get_all_values()
    result_dict = {}
    result_list_of_messages = []

    for row in table:
        if row[5] in week_dates:
            project = row[1]
            executor = row[2]
            main_key = row[4]
            seasonality = row[5]
            link = row[13]
            record = (executor, main_key, seasonality, link)
            if project in result_dict:
                result_dict[project].append(record)
            else:
                result_dict[project] = [record]

    for project_type in result_dict:
        positions_dict = get_search_positions(project_type)
        head_message = f"*{project_type} — сезонные пики на неделе\n*"
        body_message = ""
        for executor, main_key, seasonality, link in result_dict[project_type]:
            positions_string = find_positions(main_key, positions_dict=positions_dict)
            body_message += f"\n[{main_key}]({link}) | {executor} | " + positions_string

        message = head_message + body_message
        result_list_of_messages.append(message)

    return result_list_of_messages


def get_data_month(month):
    """
    Получает данные за указанный месяц и формирует сообщения для каждого проекта.

    :param month: Кортеж, содержащий номер месяца и его строковое представление ('7', '07')
    :return: Словарь, содержащий сообщения о проектах и их активности за указанный месяц
    """
    get_creds()
    # Путь к файлу credentials.json
    creds_file = 'credentials.json'
    month_name = get_month_name(month[0])

    # Авторизация и подключение к Google Sheets
    creds = Credentials.from_service_account_file(
        creds_file,
        scopes=['https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive']
    )
    client = gspread.authorize(creds)

    # Открой таблицу по ее URL или ID
    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/19zTcjsbXsutwB_fMEJMD1k8611ZdBS1B5nj0qCT-nZ0/edit?gid=0#gid=0'
    spreadsheet = client.open_by_url(spreadsheet_url)
    # Явно выбираем лист по имени (замените 'Рабочая лента' на нужное имя)
    sheet = spreadsheet.worksheet('Рабочая лента')
    # Получаем все значения из нужных столбцов
    table = sheet.get_all_values()
    result_dict = {}
    dict_of_messages = {}

    # Регулярное выражение для проверки формата "01.11"
    pattern = r"^\d{2}\.\d{2}$"

    for row in table:
        if not re.match(pattern, row[5]):
            continue

        # Проверка на совпадение месяца
        if row[5].split(".")[1] == month[1]:
            project = row[1]
            executor = row[2]
            main_key = row[4]
            seasonality = row[5]
            link = row[13]
            record = (executor, main_key, seasonality, link)

            if project in result_dict:
                result_dict[project].append(record)
            else:
                result_dict[project] = [record]

    for project_type in result_dict:
        head_message = f"*Сезонность {project_type} | {month_name}\n*"
        body_message = ""
        sorted_records = sorted(result_dict[project_type], key=lambda x: datetime.datetime.strptime(x[2], "%d.%m"))
        for executor, main_key, seasonality, link in sorted_records:
            body_message += f"\n[{main_key}]({link}) | {executor} | {seasonality}"

        message = head_message + body_message
        dict_of_messages[project_type] = message

    return dict_of_messages


def get_month_name(month_number):
    """
    Возвращает название месяца на русском языке по его номеру.

    :param month_number: Номер месяца (1-12)
    :return: Название месяца на русском языке
    """
    months = [
        "январь", "февраль", "март", "апрель", "май", "июнь",
        "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"
    ]
    return months[month_number - 1]


def get_next_month():
    """
    Возвращает номер следующего месяца и его строковое представление.

    :return: Кортеж, содержащий номер следующего месяца и его строковое представление ('7', '07')
    """
    this_month = datetime.date.today().month
    next_month = this_month + 1 if this_month != 12 else 1
    next_month_str = str(next_month) if next_month // 10 == 1 else '0' + str(next_month)
    result = (next_month, next_month_str)

    return result


def split_message(message, max_length=4096):
    """
    Функция для разбивания сообщения на несколько частей.

    :param message: Исходное сообщение
    :param max_length: Максимальная длина части сообщения
    :return: Список частей сообщения
    """
    parts = []
    while len(message) > max_length:
        split_index = message.rfind('\n', 0, max_length)
        if split_index == -1:
            split_index = max_length
        parts.append(message[:split_index])
        message = message[split_index:]
    parts.append(message)
    return parts


def get_dates_of_current_week():
    """
    Возвращает даты текущей недели в формате 'дд.мм'.

    :return: Множество дат текущей недели
    """
    # Определим текущую дату
    today = datetime.date.today()

    # Определим номер сегодняшнего дня недели (понедельник = 0, воскресенье = 6)
    start_of_week = today - datetime.timedelta(days=today.weekday())

    # Создадим множество для хранения дат в формате "дд.мм"
    dates_of_week = set()

    # Заполним множество датами текущей недели
    for i in range(7):
        current_day = start_of_week + datetime.timedelta(days=i)
        formatted_date = current_day.strftime("%d.%m")
        dates_of_week.add(formatted_date)

    return dates_of_week


def get_creds():
    """
    Получает данные учетных записей из удаленного файла и сохраняет их в локальный файл credentials.json.
    """
    url = "https://miliutin.ru/public-files/metrika-script-api-bc6a4b98dfd8.json"
    response = requests.get(url)

    # Проверяем, что запрос прошел успешно
    if response.status_code == 200:
        data = response.json()  # Считываем JSON данные из ответа

        # Записываем JSON данные в локальный файл
        with open('credentials.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        print("Файл успешно записан.")
    else:
        print(f"Не удалось скачать файл. Статус код: {response.status_code}")


def get_search_positions(project: str,):
    project_id = project_ids[project]["id"]
    last_days_list = get_last_days_date()
    url = "https://api.topvisor.com/v2/json/get/positions_2/history"
    # Define the headers
    headers = {
        "User-Id": "315804",
        "Authorization": "e0b1f4eb3a499f05615880095d91878f",
        "Content-Type": "application/json"
    }

    # Define the payload
    payload = {
        "project_id": f"{project_id}",
        "regions_indexes": [1988, 3798],
        "dates": last_days_list,
        "type_range": 4

    }
    # Send the request
    response_json = requests.get(url, headers=headers, json=payload).json()
    return create_position_dict(response_json)


def create_position_dict(data):
    position_dict = {}
    for keyword in data['result']['keywords']:
        name = keyword['name']
        positions = keyword['positionsData']
        position_dict[name] = positions
    return position_dict


def get_last_days_date(days=10):
    today = datetime.datetime.today()
    last_days = [(today - datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, days)]
    return last_days


def find_positions(name, positions_dict):
    processed_string = process_string(name)
    yandex_position = ""
    google_position = ""
    if processed_string in positions_dict:
        for _ in positions_dict[processed_string]:
            if _[-4:] == "1988":
                yandex_position = positions_dict[processed_string][_]["position"]
            else:
                google_position = positions_dict[processed_string][_]["position"]
        result_string = yandex_position + 'Я, ' + google_position + 'Г'
    else:
        result_string = "--Я, --Г"
    return result_string


def process_string(input_string):
    """
    Приводит строку к нижнему регистру и удаляет пробелы слева и справа.

    :param input_string: Входная строка
    :return: Обработанная строка
    """
    # Удаляем пробелы слева и справа, приводим к нижнему регистру
    processed_string = input_string.strip().lower()
    return processed_string
