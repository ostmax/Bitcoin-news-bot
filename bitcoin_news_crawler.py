#!/usr/bin/env python3
"""
Специализированный сборщик новостей о биткоине и криптовалютах
"""

import asyncio
import aiohttp
import feedparser
from datetime import datetime
import logging
from typing import List, Dict
import re

class BitcoinNewsCrawler:
    def __init__(self):
        # Специализированные RSS-ленты о биткоине и криптовалютах
        self.bitcoin_feeds = [
            # Основные крипто-издания
            'https://cointelegraph.com/rss',
            'https://news.bitcoin.com/feed/',
            'https://cryptopotato.com/feed/',
            'https://cryptoslate.com/feed/',
            'https://decrypt.co/feed',
            
            # Финансовые издания с крипто-разделами
            'https://coindesk.com/arc/outboundfeeds/rss/',
            'https://www.investing.com/rss/news_301.rss',  # Bitcoin News
            'https://www.investing.com/rss/news_302.rss',  # Cryptocurrency News
            
            # Технические и аналитические источники
            'https://bitcoinmagazine.com/.rss/full/',
            'https://www.coindesk.com/arc/outboundfeeds/rss/',
            
            # Международные источники
            'https://beincrypto.com/feed/',
            'https://u.today/rss',
            'https://zycrypto.com/feed/',
        ]
        
        # Ключевые слова для фильтрации биткоин-новостей
        self.bitcoin_keywords = {
            'bitcoin', 'btc', 'crypto', 'cryptocurrency', 'blockchain',
            'satoshi', 'halving', 'mining', 'bitcoin etf', 'bitcoin spot etf',
            'digital gold', 'store of value', 'bitcoin price', 'btc price',
            'lightning network', 'bitcoin wallet', 'bitcoin exchange',
            'crypto market', 'digital currency', 'decentralized'
        }
        
        # Альтернативные ключевые слова (для расширенного поиска)
        self.alternative_keywords = {
            'ethereum', 'eth', 'altcoin', 'defi', 'web3', 'nft',
            'binance', 'coinbase', 'kraken', 'crypto exchange'
        }
        
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
    
    def is_bitcoin_news(self, title: str, summary: str = "") -> bool:
        """Проверяем, относится ли новость к биткоину/криптовалютам"""
        text = f"{title} {summary}".lower()
        
        # Проверяем основные ключевые слова
        if any(keyword in text for keyword in self.bitcoin_keywords):
            return True
        
        # Проверяем альтернативные ключевые слова (опционально)
        if any(keyword in text for keyword in self.alternative_keywords):
            return True
        
        return False
    
    def extract_crypto_tickers(self, text: str) -> List[str]:
        """Извлекает крипто-тикеры из текста"""
        # Паттерн для крипто-тикеров (BTC, ETH, ADA и т.д.)
        crypto_pattern = r'\b(BTC|ETH|XRP|ADA|DOT|SOL|MATIC|LTC|BCH|XLM|LINK|UNI|DOGE|SHIB|AVAX|ATOM|ETC|XMR|EOS|TRX|ALGO|FIL|ICP|VET|THETA|XTZ|AAVE|COMP|MKR|YFI|SNX|CRV|SUSHI|BAT|ZEC|DASH|NEO|IOTA)\b'
        
        found_tickers = re.findall(crypto_pattern, text.upper())
        return list(set(found_tickers))
    
    async def fetch_bitcoin_feed(self, session: aiohttp.ClientSession, url: str) -> List[Dict]:
        """Асинхронное получение RSS-ленты с фильтрацией по биткоину"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15), headers=headers) as response:
                content = await response.text()
                feed = feedparser.parse(content)
                
                articles = []
                for entry in feed.entries:
                    # Парсим дату публикации
                    published_time = entry.get('published_parsed')
                    if published_time:
                        published_dt = datetime(*published_time[:6])
                    else:
                        published_dt = datetime.now()
                    
                    title = entry.title.strip()
                    summary = entry.get('summary', '')
                    
                    # Фильтруем только биткоин-новости
                    if not self.is_bitcoin_news(title, summary):
                        continue
                    
                    # Извлекаем крипто-тикеры
                    crypto_tickers = self.extract_crypto_tickers(f"{title} {summary}")
                    
                    article = {
                        'title': title,
                        'summary': summary,
                        'link': entry.link,
                        'published': published_dt.isoformat(),
                        'source': url,
                        'timestamp': datetime.now().isoformat(),
                        'crypto_tickers': crypto_tickers,
                        'is_bitcoin_news': True,
                    }
                    articles.append(article)
                
                self.logger.info(f"✅ Собрано {len(articles)} биткоин-новостей из {url}")
                return articles
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка при загрузке {url}: {e}")
            return []
    
    async def crawl_all_bitcoin_feeds(self) -> List[Dict]:
        """Сбор всех биткоин-новостей"""
        self.logger.info("🚀 Начинаю сбор биткоин-новостей...")
        
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_bitcoin_feed(session, feed) for feed in self.bitcoin_feeds]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            all_articles = []
            for articles in results:
                if isinstance(articles, list):
                    all_articles.extend(articles)
            
            # Сортируем по дате (сначала свежие)
            sorted_articles = sorted(all_articles, 
                                   key=lambda x: x.get('published', ''), 
                                   reverse=True)
            
            self.logger.info(f"📊 Сбор завершен: {len(sorted_articles)} биткоин-новостей")
            return sorted_articles
    
    def analyze_bitcoin_sentiment(self, title: str, summary: str = "") -> Dict:
        """Анализ тональности биткоин-новостей"""
        text = f"{title} {summary}".lower()
        
        # Ключевые слова для позитивного/негативного анализа
        positive_indicators = {
            'bullish', 'rally', 'surge', 'breakout', 'adoption', 'institutional',
            'approval', 'green light', 'partnership', 'integration', 'all time high',
            'record high', 'break through', 'momentum', 'optimistic', 'positive'
        }
        
        negative_indicators = {
            'bearish', 'crash', 'plunge', 'selloff', 'rejection', 'delay',
            'regulation', 'ban', 'warning', 'investigation', 'lawsuit',
            'hack', 'exploit', 'dump', 'fud', 'correction', 'resistance'
        }
        
        positive_score = sum(1 for word in positive_indicators if word in text)
        negative_score = sum(1 for word in negative_indicators if word in text)
        
        if positive_score > negative_score:
            sentiment = "bullish"
        elif negative_score > positive_score:
            sentiment = "bearish"
        else:
            sentiment = "neutral"
        
        return {
            'sentiment': sentiment,
            'positive_score': positive_score,
            'negative_score': negative_score,
            'total_score': positive_score - negative_score
        }