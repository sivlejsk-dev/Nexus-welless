"""
Social media ingestion - Twitter/X, Reddit, StockTwits, sentiment APIs.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from urllib.parse import urlencode

import httpx

from .base import BaseDataSource
from .schemas import MarketEvent, DataSource, EventType

log = logging.getLogger(__name__)


class TwitterSource(BaseDataSource):
    """Twitter/X API v2 integration for financial tweets"""

    BASE_URL = "https://api.twitter.com/2"

    def __init__(self, config, bearer_token: Optional[str] = None):
        super().__init__(config)
        self.source_type = DataSource.TWITTER
        self.bearer_token = bearer_token or config.twitter_bearer_token
        self._client: Optional[httpx.AsyncClient] = None
        self.financial_keywords = [
            'stock', 'earnings', 'buy', 'sell', 'call', 'put',
            'market', 'trading', 'invest', 'breakout', 'support',
            'resistance', 'dividend', 'merger', 'acquisition',
            '$', '🚀', '📈', '📉', '🔥'
        ]

    async def connect(self) -> bool:
        if not self.bearer_token:
            log.warning("Twitter bearer token not configured")
            return False
        self._client = httpx.AsyncClient(
            timeout=30.0,
            headers={'Authorization': f'Bearer {self.bearer_token}'}
        )
        return True

    async def fetch_events(self, since: Optional[datetime] = None) -> List[MarketEvent]:
        if not self._client:
            await self.connect()
        if not self._client:
            return []

        events = []
        
        try:
            # Search recent tweets about stocks/finance
            query = ' OR '.join(self.financial_keywords[:10])  # Build OR query
            params = {
                'query': query,
                'max_results': 100,
                'tweet.fields': 'created_at,author_id,public_metrics,context_annotations',
                'expansions': 'author_id',
            }
            
            response = await self._client.get(
                f"{self.BASE_URL}/tweets/search/recent",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                tweets = data.get('data', [])
                users = {u['id']: u for u in data.get('includes', {}).get('users', [])}
                
                for tweet in tweets:
                    event = self._parse_tweet(tweet, users)
                    if event and (not since or event.published_at > since):
                        events.append(event)
            
            elif response.status_code == 429:
                log.warning("Twitter API rate limit reached")
            
            else:
                log.error(f"Twitter API error: {response.status_code}")
                self.record_error()
                
        except Exception as e:
            log.error(f"Twitter fetch failed: {e}")
            self.record_error()
        
        self.mark_fetched(len(events))
        return events

    def _parse_tweet(self, tweet: Dict[str, Any], users: Dict[str, Any]) -> Optional[MarketEvent]:
        try:
            text = tweet.get('text', '')
            tweet_id = tweet.get('id')
            created_at = tweet.get('created_at')
            
            if not text:
                return None
            
            from dateutil import parser as date_parser
            published_at = datetime.utcnow()
            if created_at:
                try:
                    published_at = date_parser.parse(created_at).replace(tzinfo=None)
                except:
                    pass
            
            author_info = users.get(tweet.get('author_id'), {})
            author = author_info.get('username')
            
            # Extract tickers from tweet text
            tickers = self.extract_tickers(text)
            
            # Metrics
            metrics = tweet.get('public_metrics', {})
            metadata = {
                'retweets': metrics.get('retweet_count', 0),
                'likes': metrics.get('like_count', 0),
                'replies': metrics.get('reply_count', 0),
                'quote_count': metrics.get('quote_count', 0),
                'followers': author_info.get('public_metrics', {}).get('followers_count', 0),
            }
            
            # Detect viral spread
            is_viral = (
                metadata['retweets'] > 1000 or 
                metadata['likes'] > 5000 or
                metadata['followers'] > 100000 and metadata['likes'] > 100
            )
            
            return MarketEvent(
                source=self.source_type,
                source_id=f"tw_{tweet_id}",
                title=text[:100],  # Shortened for social
                description=text[:2000],
                url=f"https://twitter.com/user/status/{tweet_id}",
                author=author,
                published_at=published_at,
                raw_content=text,
                language="en",
                tags=['social_media', 'viral' if is_viral else 'social'],
                metadata=metadata
            )
        except Exception as e:
            log.debug(f"Tweet parse error: {e}")
            return None

    async def health_check(self) -> bool:
        if not self._client or not self.bearer_token:
            return False
        try:
            response = await self._client.get(f"{self.BASE_URL}/tweets", params={'ids': '1'})
            return response.status_code in (200, 404)  # 404 is fine (tweet doesn't exist) - API is accessible
        except:
            return False


class RedditSource(BaseDataSource):
    """Reddit API integration for stock-related subreddits"""

    BASE_URL = "https://oauth.reddit.com"

    SUBREDDITS = [
        'wallstreetbets',
        'stocks',
        'investing',
        'options',
        'pennystocks',
        'SecurityAnalysis',
        'ValueInvesting',
    ]

    def __init__(self, config, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        super().__init__(config)
        self.source_type = DataSource.REDDIT
        self.client_id = client_id or config.reddit_client_id
        self.client_secret = client_secret  # Typically from env
        self.access_token: Optional[str] = None
        self._client: Optional[httpx.AsyncClient] = None

    async def connect(self) -> bool:
        if not self.client_id or not self.client_secret:
            log.warning("Reddit credentials not configured")
            return False
        
        try:
            # OAuth2 client credentials flow
            auth = httpx.BasicAuth(self.client_id, self.client_secret)
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    'https://www.reddit.com/api/v1/access_token',
                    data={'grant_type': 'client_credentials'},
                    auth=auth,
                    headers={'User-Agent': 'NexusMarketIntel/1.0'}
                )
                if response.status_code == 200:
                    data = response.json()
                    self.access_token = data.get('access_token')
                    self._client = httpx.AsyncClient(
                        timeout=30.0,
                        headers={
                            'Authorization': f'Bearer {self.access_token}',
                            'User-Agent': 'NexusMarketIntel/1.0'
                        }
                    )
                    return True
        except Exception as e:
            log.error(f"Reddit auth failed: {e}")
        return False

    async def fetch_events(self, since: Optional[datetime] = None) -> List[MarketEvent]:
        if not self._client:
            await self.connect()
        if not self._client:
            return []

        events = []
        
        for subreddit in self.SUBREDDITS:
            try:
                # Fetch hot posts
                response = await self._client.get(
                    f"{self.BASE_URL}/r/{subreddit}/hot",
                    params={'limit': 50}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get('data', {}).get('children', [])
                    
                    for post in posts:
                        post_data = post.get('data', {})
                        event = self._parse_post(post_data, subreddit)
                        if event and (not since or event.published_at > since):
                            events.append(event)
                            
                elif response.status_code == 429:
                    log.warning("Reddit API rate limit reached")
                    break
                    
            except Exception as e:
                log.error(f"Reddit r/{subreddit} fetch error: {e}")
                continue
        
        self.mark_fetched(len(events))
        return events

    def _parse_post(self, post: Dict[str, Any], subreddit: str) -> Optional[MarketEvent]:
        try:
            title = post.get('title', '')
            selftext = post.get('selftext', '')
            url = post.get('url')
            author = post.get('author')
            created_utc = post.get('created_utc')
            score = post.get('score', 0)
            upvote_ratio = post.get('upvote_ratio', 0.5)
            num_comments = post.get('num_comments', 0)
            
            # Combine title + selftext for analysis
            full_text = f"{title}\n\n{selftext}"
            
            published_at = datetime.utcnow()
            if created_utc:
                published_at = datetime.utcfromtimestamp(created_utc)
            
            tickers = self.extract_tickers(full_text)
            
            return MarketEvent(
                source=self.source_type,
                source_id=f"reddit_{post.get('id')}",
                title=title[:200],
                description=selftext[:2000] or title[:2000],
                url=f"https://reddit.com/r/{subreddit}/comments/{post.get('id')}",
                author=author,
                published_at=published_at,
                raw_content=full_text,
                language="en",
                tags=[subreddit],
                metadata={
                    'subreddit': subreddit,
                    'score': score,
                    'upvote_ratio': upvote_ratio,
                    'num_comments': num_comments,
                    'detected_tickers': tickers,
                    'viral_score': score * upvote_ratio
                }
            )
        except:
            return None

    async def health_check(self) -> bool:
        if not self._client:
            await self.connect()
        try:
            response = await self._client.get(f"{self.BASE_URL}/r/wallstreetbets/about")
            return response.status_code == 200
        except:
            return False


class StockTwitsSource(BaseDataSource):
    """StockTwits - financial microblogging platform"""

    BASE_URL = "https://api.stocktwits.com/api/2"

    def __init__(self, config, access_token: Optional[str] = None):
        super().__init__(config)
        self.source_type = DataSource.STOCKTWITS
        self.access_token = access_token
        self._client: Optional[httpx.AsyncClient] = None
        # Trending/watched symbols
        self.watchlist = ['$AAPL', '$GOOGL', '$MSFT', '$AMZN', '$TSLA', '$NVDA', '$META']

    async def connect(self) -> bool:
        headers = {}
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        self._client = httpx.AsyncClient(timeout=30.0, headers=headers)
        return True

    async def fetch_events(self, since: Optional[datetime] = None) -> List[MarketEvent]:
        if not self._client:
            await self.connect()
        
        events = []
        
        try:
            # Fetch stream for watchlist symbols
            for symbol in self.watchlist:
                try:
                    response = await self._client.get(
                        f"{self.BASE_URL}/streams/symbol/{symbol}.json",
                        params={'limit': 30}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        messages = data.get('messages', [])
                        
                        for msg in messages:
                            event = self._parse_message(msg, symbol)
                            if event and (not since or event.published_at > since):
                                events.append(event)
                                
                except Exception as e:
                    log.debug(f"StockTwits fetch error for {symbol}: {e}")
                    continue
                    
        except Exception as e:
            log.error(f"StockTwits fetch failed: {e}")
            self.record_error()
        
        self.mark_fetched(len(events))
        return events

    def _parse_message(self, message: Dict[str, Any], symbol: str) -> Optional[MarketEvent]:
        try:
            body = message.get('body', '')
            created_at = message.get('created_at')
            user = message.get('user', {})
            message_id = message.get('id')
            
            published_at = datetime.utcnow()
            if created_at:
                from dateutil import parser as date_parser
                try:
                    published_at = date_parser.parse(created_at).replace(tzinfo=None)
                except:
                    pass
            
            return MarketEvent(
                source=self.source_type,
                source_id=f"st_{message_id}",
                title=f"StockTwits: {symbol} - {body[:80]}",
                description=body[:2000],
                author=user.get('username'),
                published_at=published_at,
                raw_content=body,
                language="en",
                tags=['stocktwits', 'sentiment'],
                metadata={
                    'symbol': symbol.replace('$', ''),
                    'user_followers': user.get('followers', 0),
                    'message_likes': message.get('likes', {}).get('count', 0),
                    'sentiment': message.get('entities', {}).get('sentiment'),
                }
            )
        except:
            return None

    async def health_check(self) -> bool:
        try:
            response = await self._client.get(f"{self.BASE_URL}/streams/trending/symbols.json")
            return response.status_code in (200, 401)  # 401 = auth needed but API reachable
        except:
            return False


class SentimentAPISource(BaseDataSource):
    """
    Aggregate sentiment from specialized financial sentiment APIs.
    Supports:
    - Finnhub sentiment
    - StockBeats
    - SocialSentiment.io
    - Custom sentiment endpoints
    """

    def __init__(self, config, provider: str = 'finnhub', api_key: Optional[str] = None):
        super().__init__(config)
        self.source_type = DataSource.SENTIMENT_API
        self.provider = provider
        self.api_key = api_key or (config.finnhub_api_key if provider == 'finnhub' else None)
        self.base_urls = {
            'finnhub': 'https://finnhub.io/api/v1',
            'stocktwits': 'https://api.stocktwits.com/api/2',
        }
        self._client: Optional[httpx.AsyncClient] = None

    async def connect(self) -> bool:
        if not self.api_key:
            log.warning(f"Sentiment API key not configured for {self.provider}")
            return False
        self._client = httpx.AsyncClient(timeout=30.0)
        return True

    async def fetch_events(self, since: Optional[datetime] = None) -> List[MarketEvent]:
        if not self._client:
            await self.connect()
        if not self._client:
            return []

        events = []
        
        if self.provider == 'finnhub':
            events = await self._fetch_finnhub_sentiment()
        elif self.provider == 'stocktwits':
            events = await self._fetch_stocktwits_sentiment()
        else:
            log.warning(f"Unknown sentiment provider: {self.provider}")
        
        self.mark_fetched(len(events))
        return events

    async def _fetch_finnhub_sentiment(self) -> List[MarketEvent]:
        """Fetch social sentiment from Finnhub"""
        events = []
        try:
            # Finnhub provides social sentiment for specific tickers
            tickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'AMD', 'INTC', 'NFLX']
            
            for ticker in tickers:
                response = await self._client.get(
                    f"{self.base_urls['finnhub']}/stock/social-sentiment",
                    params={'symbol': ticker, 'token': self.api_key}
                )
                if response.status_code == 200:
                    data = response.json()
                    for mention in data.get('mentions', [])[:5]:  # Top 5 mentions
                        event = MarketEvent(
                            source=self.source_type,
                            source_id=f"fh_{ticker}_{mention.get('id', hash(mention['title']))}",
                            title=f"Social sentiment for {ticker}: {mention.get('title', '')[:100]}",
                            description=mention.get('description', '')[:2000],
                            url=mention.get('url'),
                            published_at=datetime.utcnow(),  # Finnhub doesn't always provide precise time
                            raw_content=str(mention),
                            language="en",
                            tags=['sentiment', 'finnhub', ticker],
                            metadata={
                                'ticker': ticker,
                                'sentiment_score': mention.get('sentiment'),
                                'source': mention.get('source'),
                            }
                        )
                        events.append(event)
                elif response.status_code == 429:
                    log.warning("Finnhub rate limit reached")
                    break
        except Exception as e:
            log.error(f"Finnhub sentiment fetch failed: {e}")
            self.record_error()
        
        return events

    async def _fetch_stocktwits_sentiment(self) -> List[MarketEvent]:
        """Fetch aggregated sentiment from StockTwits"""
        events = []
        try:
            response = await self._client.get(f"{self.base_urls['stocktwits']}/streams/trending/symbols.json")
            if response.status_code == 200:
                data = response.json()
                for symbol_data in data.get('symbols', [])[:10]:
                    ticker = symbol_data.get('symbol', '')
                    sentiment = symbol_data.get('sentiment', {})
                    event = MarketEvent(
                        source=self.source_type,
                        source_id=f"st_trending_{ticker}",
                        title=f"StockTwits trending: {ticker}",
                        description=f"Sentiment: {sentiment.get('name', 'neutral')} (score: {sentiment.get('score', 0)})",
                        published_at=datetime.utcnow(),
                        raw_content=str(symbol_data),
                        tags=['sentiment', 'stocktwits', 'trending'],
                        metadata={
                            'ticker': ticker,
                            'sentiment': sentiment,
                            'watchlist_count': symbol_data.get('watchlist_count', 0),
                        }
                    )
                    events.append(event)
        except Exception as e:
            log.error(f"StockTwits sentiment fetch failed: {e}")
        
        return events

    async def health_check(self) -> bool:
        if not self._client:
            return False
        try:
            response = await self._client.get(f"{self.base_urls['finnhub']}/stock/symbol", params={'symbol': 'AAPL', 'token': self.api_key})
            return response.status_code == 200
        except:
            return False


class SocialMediaIngestor:
    """
    Orchestrates all social media sources.
    Aggregates posts from Twitter, Reddit, StockTwits and sentiment APIs.
    """

    def __init__(self, config):
        self.config = config
        self.sources: List[BaseDataSource] = []
        self.seen_post_ids: set[str] = set()
        self._initialize_sources()

    def _initialize_sources(self):
        """Initialize enabled social media sources"""
        source_map = {
            DataSource.TWITTER: lambda: TwitterSource(self.config, self.config.twitter_bearer_token),
            DataSource.REDDIT: lambda: RedditSource(self.config, self.config.reddit_client_id, None),
            DataSource.STOCKTWITS: lambda: StockTwitsSource(self.config),
            DataSource.SENTIMENT_API: lambda: SentimentAPISource(self.config, 'finnhub', self.config.finnhub_api_key),
        }

        for source_type, factory in source_map.items():
            if source_type in self.config.enabled_sources:
                try:
                    source = factory()
                    self.sources.append(source)
                except Exception as e:
                    log.warning(f"Failed to initialize {source_type}: {e}")

    async def fetch_all(self, since: Optional[datetime] = None) -> List[MarketEvent]:
        """Fetch from all social sources concurrently"""
        if not self.sources:
            log.warning("No social media sources configured")
            return []
        
        tasks = [source.fetch_events(since) for source in self.sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_events = []
        for result in results:
            if isinstance(result, Exception):
                log.error(f"Social source error: {result}")
                continue
            all_events.extend(result)
        
        # Deduplicate by content hash
        unique_events = []
        for event in all_events:
            # Use source_id as unique key
            if event.source_id not in self.seen_post_ids:
                self.seen_post_ids.add(event.source_id)
                unique_events.append(event)
        
        # Sort by engagement metrics if available, else by time
        def engagement_score(e: MarketEvent) -> float:
            metrics = e.metadata
            return (
                metrics.get('retweets', 0) * 2 +
                metrics.get('likes', 0) * 1.5 +
                metrics.get('viral_score', 0) * 3 +
                metrics.get('followers', 0) * 0.001 +
                (e.published_at - datetime(1970,1,1)).total_seconds() / 1e10  # Recency bonus
            )
        
        unique_events.sort(key=engagement_score, reverse=True)
        
        log.info(f"Social media ingestor retrieved {len(unique_events)} unique posts")
        return unique_events

    async def health_check_all(self) -> Dict[str, bool]:
        results = {}
        for source in self.sources:
            results[source.source_type.value] = await source.health_check()
        return results
