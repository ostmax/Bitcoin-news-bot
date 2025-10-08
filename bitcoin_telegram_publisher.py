#!/usr/bin/env python3
"""
Публикатор новостей в Telegram с фокусом на биткоин
"""

import asyncio
import logging
from typing import Dict, List, Optional
import aiohttp
from telegram import Bot
from telegram.error import TelegramError

class BitcoinTelegramPublisher:
    def __init__(self, bot_token: str, channel_id: str, yandex_api_key: Optional[str] = None, yandex_folder_id: Optional[str] = None):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.yandex_api_key = yandex_api_key
        self.yandex_folder_id = yandex_folder_id
        self.bot = Bot(token=bot_token)
        self.logger = logging.getLogger(__name__)
    
    async def test_connection(self):
        """Тестирование подключения к Telegram"""
        try:
            me = await self.bot.get_me()
            self.logger.info(f"✅ Бот подключен: @{me.username}")
            
            # Проверяем доступ к каналу
            try:
                chat = await self.bot.get_chat(self.channel_id)
                self.logger.info(f"✅ Канал доступен: {chat.title}")
            except Exception as e:
                self.logger.error(f"❌ Ошибка доступа к каналу {self.channel_id}: {e}")
                return False
                
            return True
        except Exception as e:
            self.logger.error(f"❌ Ошибка подключения к Telegram: {e}")
            return False
    
    async def publish_bitcoin_article(self, article: Dict) -> bool:
        """Публикация одной биткоин-новости"""
        try:
            # Форматируем сообщение
            message = self._format_bitcoin_message(article)
            
            # Публикуем в Telegram
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=False
            )
            return True
            
        except TelegramError as e:
            self.logger.error(f"❌ Ошибка Telegram при публикации: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Общая ошибка при публикации: {e}")
            return False
    
    def _format_bitcoin_message(self, article: Dict) -> str:
        """Форматирование сообщения о биткоин-новости"""
        title = article.get('title', 'Без названия')
        summary = article.get('summary', '')
        url = article.get('link', article.get('url', '#'))  # Используем link или url
        source = self._extract_source_name(article.get('source', 'Неизвестный источник'))
        
        # Эмодзи для биткоин-тематики
        emoji = self._get_crypto_emoji(article)
        
        message = f"{emoji} <b>{self._escape_html(title)}</b>\n\n"
        
        if summary and len(summary) > 50:
            # Очищаем HTML теги из summary
            import re
            clean_summary = re.sub('<[^<]+?>', '', summary)
            # Обрезаем слишком длинные описания
            if len(clean_summary) > 300:
                clean_summary = clean_summary[:300] + "..."
            message += f"{self._escape_html(clean_summary)}\n\n"
        
        message += f"🔗 <a href='{url}'>Читать полностью</a>\n"
        message += f"📰 Источник: {source}\n"
        
        # Добавляем крипто-тикеры если есть
        crypto_tickers = article.get('crypto_tickers', [])
        if crypto_tickers:
            tickers_str = " ".join([f"#{ticker}" for ticker in crypto_tickers])
            message += f"🏷️ {tickers_str}\n"
        
        # Добавляем хештеги
        message += f"#Bitcoin #BTC #Crypto #Новости"
        
        return message
    
    def _extract_source_name(self, source_url: str) -> str:
        """Извлекаем название источника из URL"""
        import re
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
            'zycrypto.com': 'ZyCrypto'
        }
        
        return source_map.get(domain, domain)
    
    def _get_crypto_emoji(self, article: Dict) -> str:
        """Выбираем эмодзи в зависимости от содержания"""
        title = article.get('title', '').lower()
        crypto_tickers = article.get('crypto_tickers', [])
        
        if 'bitcoin' in title or 'btc' in title:
            return '₿📈'
        elif 'ethereum' in title or 'eth' in title:
            return '🔷📊'
        elif any(ticker in ['ADA', 'SOL', 'DOT'] for ticker in crypto_tickers):
            return '🚀📊'
        elif 'defi' in title:
            return '🔄📈'
        elif 'nft' in title:
            return '🖼️📊'
        else:
            return '💰📰'
    
    def _escape_html(self, text: str) -> str:
        """Экранирование HTML-символов"""
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
    
    async def translate_text(self, text: str, target_language: str = "ru") -> Optional[str]:
        """Перевод текста через Yandex Translate (опционально)"""
        if not self.yandex_api_key:
            self.logger.info("⚠️ Yandex API ключ не настроен, перевод пропущен")
            return None
            
        try:
            url = "https://translate.api.cloud.yandex.net/translate/v2/translate"
            
            headers = {
                "Authorization": f"Api-Key {self.yandex_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "texts": [text],
                "targetLanguageCode": target_language,
                "folderId": self.yandex_folder_id
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        translated_text = result['translations'][0]['text']
                        self.logger.info("✅ Текст успешно переведен")
                        return translated_text
                    else:
                        error_text = await response.text()
                        self.logger.warning(f"⚠️ Ошибка перевода: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            self.logger.error(f"❌ Ошибка при переводе: {e}")
            return None

    async def publish_multiple_articles(self, articles: List[Dict]) -> int:
        """Публикация нескольких статей с задержкой"""
        published_count = 0
        
        for i, article in enumerate(articles):
            self.logger.info(f"📰 Публикация {i+1}/{len(articles)}: {article['title'][:50]}...")
            
            success = await self.publish_bitcoin_article(article)
            if success:
                published_count += 1
                self.logger.info(f"✅ Статья {i+1} опубликована")
                
                # Задержка между сообщениями чтобы не спамить
                if i < len(articles) - 1:  # Не ждем после последней статьи
                    await asyncio.sleep(3)
            else:
                self.logger.warning(f"❌ Ошибка публикации статьи {i+1}")
                
        return published_count