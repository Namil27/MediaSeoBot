#!/bin/bash

# Создаем образ, запускаем контейнер и сносим устаревший образ
docker stop media_seo_bot_cron || true
docker rm media_seo_bot_cron || true
docker build --no-cache -t mediaseobot_image:latest . && \
docker run -d --name media_seo_bot_cron mediaseobot_image:latest && \
docker image prune -a -f
