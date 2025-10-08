#!/usr/bin/env python3
"""
Пример конфигурационного файла
Замените значения на свои и переименуйте файл в config.py
"""

# Telegram Configuration
TELEGRAM_CONFIG = {
    'bot_token': 'YOUR_BOT_TOKEN_HERE',  # Получите у @BotFather
    'channel_id': '@YOUR_CHANNEL_HERE',  # Ваш канал в формате @channelname
}

# Yandex Cloud Translation API (1 млн символов/мес бесплатно)
YANDEX_CONFIG = {
    'api_key': 'YOUR_YANDEX_API_KEY_HERE',    # Получите в Yandex Cloud Console
    'folder_id': 'YOUR_FOLDER_ID_HERE',       # ID каталога в Yandex Cloud
}

# Bitcoin News Configuration
BITCOIN_CONFIG = {
    'enable_bitcoin_filtering': True,
    'min_confidence': 0.4,
    'max_posts_per_cycle': 5,
    'monitoring_interval': 30,  # минут
}