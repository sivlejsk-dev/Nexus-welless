"""
News ingestion module - RSS feeds, NewsAPI, and financial news sources.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
import xml.etree.ElementTree as ET

import httpx
from bs4 import BeautifulSoup

from .base import BaseDataSource
from .schemas import MarketEvent, DataSource, EventType

log = logging.getLogger(__name__)


class RSSNewsSource(BaseDataSource):
    """Ingest news from RSS/Atom feeds"""

    FEED_URLS = {
        'reuters_business': 'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best',
        'reuters_markets': 'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best&best-cat=markets',
        'reuters_technology': 'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best&best-cat=technology',
        'reuters_finance': 'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best&best-cat=finance',
        'yahoo_finance': 'https://finance.yahoo.com/news/rssindex',
        'cnbc_topnews': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
        'marketwatch': 'https://feeds.marketwatch.com/marketwatch/topstories',
        'seeking_alpha': 'https://seekingalpha.com/feed.xml',
        'benzinga': 'https://www.benzinga.com/feed',
    }

    def __init__(self, config, feed_url: Optional[str] = None, feed_name: Optional[str] = None):
        super().__init__(config)
        self.source_type = DataSource.NEWS_RSS
        self.feed_url = feed_url
        self.feed_name = feed_name or 'custom_rss'
        self._client: Optional[httpx.AsyncClient] = None

    async def connect(self) -> bool:
        """Initialize HTTP client"""
        try:
            self._client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
            return True
        except Exception as e:
            log.error(f"RSS source connect failed: {e}")
            return False

    async def fetch_events(self, since: Optional[datetime] = None) -> List[MarketEvent]:
        """Fetch latest news items from RSS feed"""
        if not self._client:
            await self.connect()

        url = self.feed_url or self.FEED_URLS.get(self.feed_name)
        if not url:
            log.error(f"No RSS URL for feed: {self.feed_name}")
            return []

        try:
            response = await self._client.get(url)
            response.raise_for_status()
            
            events = []
            root = ET.fromstring(response.content)
            
            # Parse RSS 2.0 or Atom
            items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
            
            for item in items:
                event = self._parse_item(item, url)
                if event and (not since or event.published_at > since):
                    events.append(event)
            
            self.mark_fetched(len(events))
            log.info(f"Fetched {len(events)} items from {self.feed_name}")
            return events
            
        except Exception as e:
            log.error(f"RSS fetch failed for {self.feed_name}: {e}")
            self.record_error()
            return []

    def _parse_item(self, item: ET.Element, feed_url: str) -> Optional[MarketEvent]:
        """Parse RSS/Atom item into MarketEvent"""
        try:
            # Extract fields with multiple possible paths
            def get_text(paths: List[str]) -> Optional[str]:
                for path in paths:
                    elem = item.find(path)
                    if elem is not None and elem.text:
                        return elem.text.strip()
                return None

            title = get_text(['title', '{http://www.w3.org/2005/Atom}title'])
            link = get_text(['link', '{http://www.w3.org/2005/Atom}link'])
            description = get_text(['description', '{http://www.w3.org/2005/Atom}summary'])
            author = get_text(['author', '{http://www.w3.org/2005/Atom}author', '{http://www.w3.org/2005/Atom}contributor'])
            pub_date = get_text(['pubDate', '{http://www.w3.org/2005/Atom}published', '{http://www.w3.org/2005/Atom}updated'])

            if not title or not description:
                return None

            # Parse date
            from dateutil import parser as date_parser
            published_at = datetime.utcnow()
            if pub_date:
                try:
                    published_at = date_parser.parse(pub_date)
                    if published_at.tzinfo:
                        published_at = published_at.astimezone(None).replace(tzinfo=None)
                except:
                    pass

            # Generate unique ID from title+link
            source_id = link or title
            event_id_hash = hashlib.md5(f"{feed_url}:{source_id}".encode()).hexdigest()[:12]

            # Extract tickers from title/description
            combined_text = f"{title} {description}"
            tickers = self.extract_tickers(combined_text)

            # Categorize event type from title keywords
            event_type = self._categorize_event_type(title, description)

            return MarketEvent(
                source=self.source_type,
                source_id=event_id_hash,
                title=title[:500],
                description=description[:2000],
                url=link,
                author=author,
                published_at=published_at,
                raw_content=f"{title}\n\n{description}",
                language="en",
                tags=[event_type],
                metadata={
                    'feed': self.feed_name,
                    'feed_url': feed_url,
                    'event_type_hint': event_type,
                    'detected_tickers': tickers,
                }
            )
        except Exception as e:
            log.debug(f"Failed to parse RSS item: {e}")
            return None

    def _categorize_event_type(self, title: str, description: str) -> str:
        """Quick keyword-based categorization (full classifier runs later)"""
        text = (title + ' ' + description).lower()
        
        mappings = {
            'earnings': ['earnings', 'eps', 'q1', 'q2', 'q3', 'q4', 'quarterly', 'beat', 'miss'],
            'ma': ['merger', 'acquisition', 'acquire', 'buyout', 'deal', 'merger'],
            'regulatory': ['regulatory', 'fda', 'sec', 'approval', 'granted', 'rejected', 'lawsuit'],
            'product_launch': ['launch', 'announce', 'unveil', 'release', 'new product'],
            'management_change': ['ceo', 'executive', 'appoint', 'resign', 'management shuffle'],
            'legal': ['lawsuit', 'litigation', 'settlement', 'patent', 'court'],
            'macro': ['fed', 'interest rate', 'inflation', 'cpi', 'gdp', 'unemployment', 'jobs'],
            'analyst_upgrade': ['upgrade', 'downgrade', 'rating', 'analyst', 'target price'],
        }
        
        for event_type, keywords in mappings.items():
            if any(kw in text for kw in keywords):
                return event_type
        
        return 'news_general'

    async def health_check(self) -> bool:
        """Verify RSS feed is accessible"""
        url = self.feed_url or list(self.FEED_URLS.values())[0]
        try:
            if not self._client:
                self._client = httpx.AsyncClient(timeout=10.0)
            response = await self._client.get(url, timeout=10.0)
            return response.status_code == 200
        except:
            return False


class NewsAPISource(BaseDataSource):
    """Ingest news from NewsAPI (newsapi.org)"""

    def __init__(self, config, api_key: Optional[str] = None):
        super().__init__(config)
        self.source_type = DataSource.NEWS_API
        self.api_key = api_key or config.newsapi_key
        self.base_url = "https://newsapi.org/v2"
        self._client: Optional[httpx.AsyncClient] = None

    async def connect(self) -> bool:
        if not self.api_key:
            log.warning("NewsAPI key not configured")
            return False
        self._client = httpx.AsyncClient(timeout=30.0)
        return True

    async def fetch_events(self, since: Optional[datetime] = None) -> List[MarketEvent]:
        if not self._client:
            await self.connect()
        if not self._client:
            return []

        events = []
        
        # Query parameters
        params = {
            'apiKey': self.api_key,
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': 100,
        }
        
        if since:
            params['from'] = since.strftime('%Y-%m-%dT%H:%M:%S')
        
        # Fetch business/finance news
        categories = ['business', 'technology', 'general']
        
        for category in categories:
            try:
                params['category'] = category
                response = await self._client.get(f"{self.base_url}/top-headlines", params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    for article in data.get('articles', []):
                        event = self._parse_article(article)
                        if event:
                            events.append(event)
                elif response.status_code == 429:
                    log.warning("NewsAPI rate limit reached")
                    break
                    
            except Exception as e:
                log.error(f"NewsAPI fetch error: {e}")
                self.record_error()
        
        self.mark_fetched(len(events))
        return events

    def _parse_article(self, article: Dict[str, Any]) -> Optional[MarketEvent]:
        try:
            title = article.get('title', '')[:500]
            description = article.get('description', '')[:2000]
            url = article.get('url')
            author = article.get('author')
            published_at_str = article.get('publishedAt')
            
            if not title or not description:
                return None
            
            published_at = datetime.utcnow()
            if published_at_str:
                from dateutil import parser as date_parser
                try:
                    published_at = date_parser.parse(published_at_str)
                except:
                    pass
            
            source_id = hashlib.md5(f"{url or title}".encode()).hexdigest()[:12]
            tickers = self.extract_tickers(title + ' ' + description)
            event_type = self._categorize_event_type(title, description)
            
            return MarketEvent(
                source=self.source_type,
                source_id=source_id,
                title=title,
                description=description,
                url=url,
                author=author,
                published_at=published_at,
                raw_content=f"{title}\n\n{description}",
                language="en",
                tags=[event_type],
                metadata={
                    'source_name': article.get('source', {}).get('name'),
                    'detected_tickers': tickers,
                }
            )
        except:
            return None

    def _categorize_event_type(self, title: str, description: str) -> str:
        return RSSNewsSource._categorize_event_type(self, title, description)

    async def health_check(self) -> bool:
        if not self._client or not self.api_key:
            return False
        try:
            response = await self._client.get(f"{self.base_url}/top-headlines", params={'apiKey': self.api_key, 'pageSize': 1})
            return response.status_code in (200, 426)  # 426 = rate limit exceeded (still accessible)
        except:
            return False


class 财经新闻Source(BaseDataSource):
    """
    Chinese financial news aggregator.
    Fetches from multiple Chinese financial news sources:
    - 东方财富网 (eastmoney.com)
    - 新浪财经 (finance.sina.com.cn)
    - 财联社 (cls.cn)
    - 金十数据 (jin10.com)
    """

    def __init__(self, config):
        super().__init__(config)
        self.source_type = DataSource.NEWS_财经
        self._client: Optional[httpx.AsyncClient] = None
        
        self.endpoints = {
            'eastmoney': 'https://finance.eastmoney.com/a/cywgg.html',  # Company news
            'sina': 'https://finance.sina.com.cn/stock/',  # Stock news
            # Additional sources would require specialized APIs or scraping
        }

    async def connect(self) -> bool:
        self._client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        return True

    async def fetch_events(self, since: Optional[datetime] = None) -> List[MarketEvent]:
        if not self._client:
            await self.connect()
        
        events = []
        
        # Scrape major Chinese financial news portals
        for source_name, url in self.endpoints.items():
            try:
                response = await self._client.get(url, headers={'User-Agent': 'Mozilla/5.0'})
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract news headlines/links - structure varies by site
                    # This is a simplified generic extraction
                    headlines = soup.find_all(['h1', 'h2', 'h3', 'a'])
                    for headline in headlines[:20]:  # Limit per source
                        text = headline.get_text(strip=True)
                        if len(text) < 10:
                            continue
                        
                        link = headline.get('href')
                        if link and not link.startswith('http'):
                            link = url.rsplit('/', 1)[0] + '/' + link.lstrip('/')
                        
                        event = MarketEvent(
                            source=self.source_type,
                            source_id=f"{source_name}_{hashlib.md5(text.encode()).hexdigest()[:8]}",
                            title=text[:200],
                            description=text[:1000],
                            url=link,
                            published_at=datetime.utcnow(),
                            raw_content=text,
                            language="zh",
                            tags=['chinese_financial'],
                            metadata={'source': source_name}
                        )
                        events.append(event)
                        
            except Exception as e:
                log.debug(f"Failed to fetch from {source_name}: {e}")
                continue
        
        self.mark_fetched(len(events))
        return events

    async def health_check(self) -> bool:
        """Check if news sources are accessible"""
        if not self._client:
            return False
        try:
            response = await self._client.get('https://finance.eastmoney.com', timeout=10.0)
            return response.status_code == 200
        except:
            return False


class NewsIngestor:
    """
    Main news ingestion orchestrator.
    Manages multiple news sources and deduplicates events.
    """

    def __init__(self, config):
        self.config = config
        self.sources: List[BaseDataSource] = []
        self.seen_event_ids: set[str] = set()
        self._initialize_sources()

    def _initialize_sources(self):
        """Initialize configured news sources"""
        source_configs = {
            DataSource.NEWS_RSS: [
                ('reuters_business', 'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best'),
                ('reuters_markets', 'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best&best-cat=markets'),
                ('reuters_finance', 'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best&best-cat=finance'),
                ('yahoo_finance', 'https://finance.yahoo.com/news/rssindex'),
                ('marketwatch', 'https://feeds.marketwatch.com/marketwatch/topstories'),
            ],
            DataSource.NEWS_API: [('newsapi', self.config.newsapi_key)],
            DataSource.NEWS_财经: [('财经', None)],
        }

        for source_type, instances in source_configs.items():
            if source_type in self.config.enabled_sources:
                for name, url_or_key in instances:
                    if source_type == DataSource.NEWS_RSS:
                        source = RSSNewsSource(self.config, feed_url=url_or_key, feed_name=name)
                        self.sources.append(source)
                    elif source_type == DataSource.NEWS_API and url_or_key:
                        source = NewsAPISource(self.config, api_key=url_or_key)
                        self.sources.append(source)
                    elif source_type == DataSource.NEWS_财经:
                        source = 财经新闻Source(self.config)
                        self.sources.append(source)

    async def fetch_all(self, since: Optional[datetime] = None) -> List[MarketEvent]:
        """Fetch from all sources concurrently"""
        if not self.sources:
            log.warning("No news sources configured")
            return []
        
        tasks = [source.fetch_events(since) for source in self.sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_events = []
        for result in results:
            if isinstance(result, Exception):
                log.error(f"News source error: {result}")
                continue
            all_events.extend(result)
        
        # Deduplicate
        unique_events = []
        for event in all_events:
            dedup_key = f"{event.source.value}:{event.source_id}"
            if dedup_key not in self.seen_event_ids:
                self.seen_event_ids.add(dedup_key)
                unique_events.append(event)
        
        # Sort by published time (newest first)
        unique_events.sort(key=lambda e: e.published_at, reverse=True)
        
        log.info(f"News ingestor retrieved {len(unique_events)} unique events")
        return unique_events

    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all sources"""
        results = {}
        for source in self.sources:
            results[source.source_type.value] = await source.health_check()
        return results
