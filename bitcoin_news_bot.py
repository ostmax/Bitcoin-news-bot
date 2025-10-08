#!/usr/bin/env python3
"""
Основной бот для сбора и публикации биткоин-новостей с переводом и анализом влияния
"""

import asyncio
import logging
import re
from typing import Dict, List
from bitcoin_news_crawler import BitcoinNewsCrawler
from bitcoin_telegram_publisher import BitcoinTelegramPublisher
from config import TELEGRAM_CONFIG, YANDEX_CONFIG, BITCOIN_CONFIG

class BitcoinNewsBot:
    def __init__(self):
        self.crawler = BitcoinNewsCrawler()
        self.publisher = BitcoinTelegramPublisher(
            TELEGRAM_CONFIG['bot_token'],
            TELEGRAM_CONFIG['channel_id'],
            YANDEX_CONFIG.get('api_key'),
            YANDEX_CONFIG.get('folder_id')
        )
        
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def clean_text(self, text: str) -> str:
        """Очистка текста от HTML тегов и лишних пробелов"""
        if not text:
            return ""
        # Удаляем HTML теги
        clean = re.sub('<[^<]+?>', '', text)
        # Удаляем лишние пробелы
        clean = re.sub('\s+', ' ', clean).strip()
        return clean
    
    def analyze_price_impact(self, title: str, summary: str) -> str:
        """Анализ потенциального влияния новости на цену биткоина"""
        text = f"{title} {summary}".lower()
        
        # Сильные позитивные сигналы
        strong_positive = {
            'approval', 'approved', 'adoption', 'institutional', 'etf approved',
            'breakthrough', 'rally', 'surge', 'bullish', 'partnership',
            'integration', 'all time high', 'record high', 'adopted',
            'halving', 'institutional adoption', 'mass adoption'
        }
        
        # Умеренные позитивные сигналы
        moderate_positive = {
            'positive', 'growth', 'expansion', 'development', 'progress',
            'innovation', 'upgrade', 'improvement', 'partnership', 'uptrend'
        }
        
        # Сильные негативные сигналы
        strong_negative = {
            'ban', 'banned', 'rejection', 'rejected', 'regulation', 'crackdown',
            'lawsuit', 'investigation', 'hack', 'exploit', 'crash', 'plunge',
            'selloff', 'fraud', 'scam', 'security breach', 'market crash'
        }
        
        # Умеренные негативные сигналы
        moderate_negative = {
            'delay', 'warning', 'concern', 'risk', 'volatility', 'uncertainty',
            'correction', 'resistance', 'pressure', 'downtrend', 'bearish'
        }
        
        # Нейтральные/технические
        neutral = {
            'analysis', 'report', 'update', 'announcement', 'news',
            'development', 'feature', 'technical', 'maintenance'
        }
        
        # Подсчет баллов
        positive_score = sum(1 for word in strong_positive if word in text) * 2
        positive_score += sum(1 for word in moderate_positive if word in text)
        
        negative_score = sum(1 for word in strong_negative if word in text) * 2
        negative_score += sum(1 for word in moderate_negative if word in text)
        
        # Определение влияния
        if positive_score > negative_score:
            if positive_score >= 3:
                return "📈 Сильное влияние | Прогноз: +3-7%"
            else:
                return "📈 Умеренное влияние | Прогноз: +1-3%"
        elif negative_score > positive_score:
            if negative_score >= 3:
                return "📉 Сильное влияние | Прогноз: -3-7%"
            else:
                return "📉 Умеренное влияние | Прогноз: -1-3%"
        else:
            return "➡️ Минимальное влияние | Прогноз: ±1%"
    
    async def translate_article(self, article: Dict) -> Dict:
        """Перевод заголовка новости"""
        try:
            # Переводим только заголовок
            title_ru = await self.publisher.translate_text(article['title'])
            if title_ru:
                article['title_ru'] = title_ru
            else:
                article['title_ru'] = article['title']
            
            return article
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка перевода: {e}")
            article['title_ru'] = article['title']
            return article
    
    def format_minimalistic_message(self, article: Dict) -> str:
        """Форматирование новости в минималистичном стиле (только заголовок)"""
        # Используем переведенный заголовок или оригинальный
        title = article.get('title_ru', article['title'])
        title = self.clean_text(title)
        
        # Анализ влияния на цену
        price_impact = self.analyze_price_impact(
            article.get('title_ru', article['title']),
            article.get('summary', '')
        )
        
        # Форматируем дату если есть
        date_str = ""
        if article.get('published'):
            try:
                from datetime import datetime
                pub_date = datetime.fromisoformat(article['published'].replace('Z', '+00:00'))
                date_str = pub_date.strftime("📅 %d.%m %H:%M")
            except:
                date_str = "📅 Сегодня"
        
        # Источник с активной ссылкой
        source_name = self.extract_source_name(article.get('source', ''))
        article_url = article.get('link', article.get('url', ''))
        
        # Строим минималистичное сообщение
        message = f"<b>{title}</b>\n\n"
        message += f"{price_impact}\n"
        
        if date_str:
            message += f"{date_str} | "
        
        # Добавляем активную ссылку на источник
        if article_url:
            message += f'<a href="{article_url}">{source_name}</a>'
        else:
            message += f"{source_name}"
        
        # Добавляем хештеги на основе тикеров
        crypto_tickers = article.get('crypto_tickers', [])
        if crypto_tickers:
            tickers_str = " ".join([f"#{ticker}" for ticker in crypto_tickers[:3]])
            message += f"\n{tickers_str}"
        
        return message
    
    def extract_source_name(self, source_url: str) -> str:
        """Извлекаем название источника из URL"""
        # Убираем протокол и путь, оставляем домен
        domain = re.sub(r'^https?://(www\.)?', '', source_url)
        domain = domain.split('/')[0]
        
        # Сопоставляем домены с читаемыми названиями
        source_map = {
            'cointelegraph.com': 'Cointelegraph',
            'news.bitcoin.com': 'Bitcoin.com',
            'cryptopotato.com': 'CryptoPotato',
            'cryptoslate.com': 'CryptoSlate',
            'decrypt.co': 'Decrypt',
            'coindesk.com': 'CoinDesk',
            'investing.com': 'Investing.com',
            'bitcoinmagazine.com': 'Bitcoin Magazine',
            'beincrypto.com': 'BeInCrypto',
            'u.today': 'U.Today',
            'zycrypto.com': 'ZyCrypto',
            'npr.org': 'NPR',
            'reuters.com': 'Reuters',
            'bloomberg.com': 'Bloomberg',
            'cnbc.com': 'CNBC'
        }
        
        return source_map.get(domain, domain.split('.')[0].title())
    
    async def process_and_publish_article(self, article: Dict) -> bool:
        """Обработка и публикация одной новости"""
        try:
            # Переводим только заголовок новости
            translated_article = await self.translate_article(article)
            
            # Форматируем минималистичное сообщение
            message = self.format_minimalistic_message(translated_article)
            
            # Публикуем в Telegram
            await self.publisher.bot.send_message(
                chat_id=TELEGRAM_CONFIG['channel_id'],
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=True  # Убираем превью ссылок
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка публикации: {e}")
            return False
    
    async def run_bitcoin_news_cycle(self):
        """Один цикл сбора и публикации биткоин-новостей"""
        try:
            self.logger.info("🚀 Запуск цикла сбора биткоин-новостей...")
            
            # Сбор новостей
            articles = await self.crawler.crawl_all_bitcoin_feeds()
            
            if not articles:
                self.logger.warning("⚠️ Не найдено биткоин-новостей")
                return 0
            
            self.logger.info(f"📰 Найдено {len(articles)} новостей")
            
            # Применяем дополнительную фильтрацию
            if BITCOIN_CONFIG.get('enable_bitcoin_filtering', True):
                filtered_articles = []
                for article in articles:
                    title = article.get('title', '').lower()
                    summary = article.get('summary', '').lower()
                    text = f"{title} {summary}"
                    
                    # Проверяем основные биткоин ключевые слова
                    bitcoin_keywords = ['bitcoin', 'btc', 'crypto', 'cryptocurrency', 'blockchain']
                    if any(keyword in text for keyword in bitcoin_keywords):
                        filtered_articles.append(article)
                
                articles = filtered_articles
                self.logger.info(f"🔍 После фильтрации осталось {len(articles)} новостей")
            
            if not articles:
                self.logger.warning("⚠️ После фильтрации новостей не осталось")
                return 0
            
            # Ограничиваем количество постов за цикл
            max_posts = BITCOIN_CONFIG.get('max_posts_per_cycle', 5)
            articles_to_publish = articles[:max_posts]
            
            self.logger.info(f"📤 Публикую {len(articles_to_publish)} новостей...")
            
            # Публикация с переводом
            published_count = 0
            for i, article in enumerate(articles_to_publish):
                self.logger.info(f"🌐 Перевод и публикация {i+1}/{len(articles_to_publish)}...")
                
                success = await self.process_and_publish_article(article)
                if success:
                    published_count += 1
                    self.logger.info(f"✅ Новость {i+1} опубликована")
                    
                    # Задержка между сообщениями
                    if i < len(articles_to_publish) - 1:
                        await asyncio.sleep(3)
                else:
                    self.logger.warning(f"❌ Ошибка публикации новости {i+1}")
            
            self.logger.info(f"📊 Цикл завершен: опубликовано {published_count}/{len(articles_to_publish)} новостей")
            return published_count
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка в цикле сбора: {e}")
            return 0
    
    async def start_monitoring(self, interval_minutes: int = None):
        """Запуск непрерывного мониторинга"""
        if interval_minutes is None:
            interval_minutes = BITCOIN_CONFIG.get('monitoring_interval', 30)
            
        self.logger.info(f"🔍 Запуск мониторинга биткоин-новостей (интервал: {interval_minutes} мин)")
        
        cycle_count = 0
        try:
            while True:
                cycle_count += 1
                self.logger.info(f"🔄 Цикл #{cycle_count}")
                
                published = await self.run_bitcoin_news_cycle()
                
                if published == 0:
                    self.logger.info("ℹ️ Новых новостей не найдено, ждем следующий цикл")
                
                # Ждем перед следующим циклом
                self.logger.info(f"⏰ Ожидание {interval_minutes} минут...")
                await asyncio.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            self.logger.info("⏹️ Мониторинг остановлен пользователем")
        except Exception as e:
            self.logger.error(f"💥 Критическая ошибка мониторинга: {e}")
            self.logger.info("🔄 Перезапуск через 60 секунд...")
            await asyncio.sleep(60)
            await self.start_monitoring(interval_minutes)
    
    async def run_single_cycle(self):
        """Запуск одного цикла сбора и публикации"""
        self.logger.info("🔸 Запуск одиночного цикла...")
        
        await self.run_bitcoin_news_cycle()
        
        self.logger.info("✅ Одиночный цикл завершен")

async def main():
    """Основная функция"""
    print("₿ BITCOIN NEWS BOT")
    print("=" * 50)
    print("Канал: @Coffee_and_Charts")
    print("Фокус: Биткоин и криптовалюты")
    print("Перевод: Yandex Cloud API")
    print("=" * 50)
    print("\nВыберите режим работы:")
    print("1. Непрерывный мониторинг")
    print("2. Одиночный цикл")
    print("3. Тест подключения")
    
    try:
        choice = input("\nВведите номер (1-3): ").strip()
        
        bot = BitcoinNewsBot()
        
        # Тестируем подключение
        print("\n🔍 Тестируем подключение...")
        connection_ok = await bot.publisher.test_connection()
        
        if not connection_ok:
            print("❌ Не удалось подключиться к Telegram. Проверьте:")
            print(f"   - Токен бота: {'***' + TELEGRAM_CONFIG['bot_token'][-8:] if TELEGRAM_CONFIG['bot_token'] else 'НЕ НАЙДЕН'}")
            print(f"   - ID канала: {TELEGRAM_CONFIG['channel_id']}")
            print("   - Бот должен быть администратором канала")
            return
        
        print("✅ Подключение успешно!")
        
        # Проверяем Yandex API
        if YANDEX_CONFIG.get('api_key'):
            print("🔤 Yandex Translate API: Настроен")
        else:
            print("⚠️ Yandex Translate API: Не настроен (перевод недоступен)")
        
        if choice == "1":
            # Непрерывный мониторинг
            interval = input("Введите интервал в минутах [30]: ").strip()
            interval_minutes = int(interval) if interval.isdigit() else 30
            
            print(f"\n🚀 Запуск непрерывного мониторинга...")
            print(f"📊 Интервал: {interval_minutes} минут")
            print(f"📰 Максимум постов за цикл: {BITCOIN_CONFIG.get('max_posts_per_cycle', 5)}")
            print("⏹️  Для остановки нажмите Ctrl+C\n")
            
            await bot.start_monitoring(interval_minutes)
            
        elif choice == "2":
            # Одиночный цикл
            print("\n🔸 Запуск одиночного цикла...")
            await bot.run_single_cycle()
            print("\n✅ Цикл завершен!")
            
        elif choice == "3":
            # Только тест подключения
            print("✅ Тест подключения пройден успешно!")
            return
            
        else:
            print("❌ Неверный выбор. Завершение работы.")
            
    except KeyboardInterrupt:
        print("\n\n👋 Завершение работы...")
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        logging.exception("Детали ошибки:")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Завершение работы...")