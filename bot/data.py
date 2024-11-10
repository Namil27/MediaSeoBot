import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MAIN_CHAT_ID = os.getenv("MAIN_CHAT_ID")


project_ids = {
    "Тренды": {
        "id": 5286328,
        "index_google": 3798,
        "index_yandex": 1988
        },

    "Недвижимость": {
        "id": 5286369,
        "index_google": 3798,
        "index_yandex": 1988
        },

    "Life": {
        "id": 5856528,
        "index_google": 3798,
        "index_yandex": 1988
        },

    "Инвестиции": {
        "id": 5286286,
        "index_google": 3798,
        "index_yandex": 1988
        },

    "Autonews": {
        "id": 5286291,
        "index_google": 3798,
        "index_yandex": 1988
        },

    "Стиль": {
        "id": 5286765,
        "index_google": 3798,
        "index_yandex": 1988
        },
}
