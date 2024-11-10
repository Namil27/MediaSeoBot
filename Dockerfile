# Используем базовый образ Python (или другой, в зависимости от вашего проекта)
FROM python:3.11

# Установка git и cron
RUN apt-get update && apt-get install -y git cron

# Клонирование репозитория и установка зависимостей
RUN git clone https://<никнейм создателя токена>:<токен развертывания>.ru/project/maksim-i-nikita/mediaseobot.git /app \
    && cd /app \
    && pip install -r --no-cache-dir requirements.txt

# Даем права на выполнение скриптов
RUN chmod +x /app/bot/week_massage.py

RUN chmod +x /app/bot/month_massage.py

# Добавляем cron задание
COPY cron_msb /etc/cron.d/cron_msb

# Даем права на выполнение cron задания
RUN chmod 0755 /etc/cron.d/cron_msb

# Создаем файл лога
RUN touch /var/log/cron.log

# Применяем cron задание
RUN crontab /etc/cron.d/cron_msb

# Запускаем cron в фореграунд режиме и показываем логи cron
CMD cron -f && tail -f /var/log/cron.log
