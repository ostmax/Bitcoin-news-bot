# ₿ Bitcoin News Bot

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://core.telegram.org/bots)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Автоматический бот для сбора, анализа и публикации новостей о биткоине и криптовалютах в Telegram канал.

## 🚀 Возможности

- **📰 Автоматический сбор новостей** с ведущих крипто-изданий
- **🌐 Автоперевод** заголовков через Yandex Cloud Translate API
- **📊 Анализ влияния** на цену биткоина
- **🔔 Минималистичные уведомления** в Telegram
- **⏰ Непрерывный мониторинг** с настраиваемым интервалом
- **🎯 Умная фильтрация** только релевантных новостей

## 📋 Поддерживаемые источники

- Cointelegraph
- Bitcoin.com
- CoinDesk  
- Decrypt
- CryptoSlate
- BeInCrypto
- Investing.com
- И другие ведущие издания

## 🛠 Установка и настройка

### 1. Клонирование репозитория

```bash
git clone https://github.com/yourusername/bitcoin-news-bot.git
cd bitcoin-news-bot

2. Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate  # Windows

3. Установка зависимостей
pip install -r requirements.txt

4. Настройка конфигурации
cp config_example.py

🎮 Использование
Запуск бота
python bitcoin_news_bot.py

Режимы работы
Непрерывный мониторинг - автоматический сбор новостей каждые 30 минут

Одиночный цикл - разовый сбор и публикация новостей

Тест подключения - проверка корректности настроек

📁 Структура проекта
bitcoin-news-bot/
├── bitcoin_news_bot.py      # Основной бот
├── bitcoin_news_crawler.py  # Сборщик новостей
├── bitcoin_telegram_publisher.py  # Публикатор
├── config_example.py        # Пример конфигурации
├── requirements.txt         # Зависимости
├── .gitignore              # Git ignore правила
└── README.md               # Документация

🎯 Пример вывода
<b>Биткоин достиг нового максимума на фоне институционального принятия</b>

📈 Сильное влияние | Прогноз: +3-7%
📅 07.10 17:16 | Cointelegraph
#BTC #Bitcoin

🔧 Технические детали
Асинхронная архитектура - высокая производительность
Умная фильтрация - только релевантные новости
Обработка ошибок - устойчивость к сбоям
Логирование - детальный мониторинг работы

