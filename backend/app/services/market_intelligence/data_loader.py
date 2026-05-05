"""
Utilities for loading historical data into simulation repository.

Supports multiple data sources:
- Yahoo Finance (via yfinance)
- CSV files
- JSON dumps
- Database queries (future)
"""

from __future__ import annotations

import asyncio
import csv
import json
import logging
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import uuid

import httpx

from app.services.market_intelligence.schemas import MarketEvent, DataSource, EventType
from app.services.market_intelligence.classifier import EventClassifier

log = logging.getLogger(__name__)


class HistoricalDataLoader:
    """
    Loads historical market data into the simulation repository.
    
    Handles:
    - Price data (OHLCV)
    - Options chains (if available)
    - News/events from archives
    - Social sentiment archives
    """
    
    def __init__(self, repository, config):
        self.repo = repository
        self.config = config
        self.classifier = EventClassifier(config)
    
    async def load_from_yahoo(
        self,
        tickers: List[str],
        start_date: datetime,
        end_date: datetime,
        include_news: bool = True
    ) -> None:
        """
        Load historical data from Yahoo Finance.
        
        Downloads:
        - Daily price data (OHLCV)
        - Option chains (snapshots at intervals)
        - News headlines (via RSS)
        """
        try:
            import yfinance as yf
            import pandas as pd
        except ImportError:
            raise ImportError("yfinance not installed. Run: pip install yfinance")
        
        log.info(f"Loading Yahoo Finance data for {len(tickers)} tickers")
        
        price_data = {}
        events = []
        options_chains = {}
        
        for ticker in tickers:
            log.info(f"  Fetching {ticker}...")
            
            # Price data
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(start=start_date, end=end_date)
                
                if hist.empty:
                    log.warning(f"  No price data for {ticker}")
                    continue
                
                series = []
                for dt, row in hist.iterrows():
                    series.append((
                        dt.to_pydatetime().date(),
                        {
                            'open': float(row['Open']),
                            'high': float(row['High']),
                            'low': float(row['Low']),
                            'close': float(row['Close']),
                            'volume': int(row['Volume']),
                        }
                    ))
                price_data[ticker] = series
                
                # Options chain snapshots (end of month)
                # In practice, would fetch at more granular intervals
                options_snapshots = await self._fetch_options_snapshots(
                    stock, start_date, end_date, ticker
                )
                if options_snapshots:
                    options_chains.update(options_snapshots)
                
            except Exception as e:
                log.error(f"  Error fetching {ticker}: {e}")
                continue
        
        # Load news if requested
        if include_news:
            news_events = await self._load_yahoo_news(tickers, start_date, end_date)
            events.extend(news_events)
        
        # Store in repository
        self.repo.store_historical_data(events, {}, price_data, options_chains)
        log.info(f"Yahoo load complete: {len(price_data)} tickers, {len(events)} events")
    
    async def _fetch_options_snapshots(
        self,
        stock,
        start_date: datetime,
        end_date: datetime,
        ticker: str
    ) -> Dict[date, List[Dict]]:
        """Fetch options chain snapshots at monthly intervals"""
        chains = {}
        
        try:
            # Get all expiry dates available
            expirations = stock.options
            if not expirations:
                return {}
            
            # Take snapshots at start, middle, end of period
            from datetime import timedelta
            
            snapshot_dates = [
                start_date.date(),
                start_date.date() + (end_date.date() - start_date.date()) // 2,
                end_date.date(),
            ]
            
            for snapshot_date in snapshot_dates:
                # Find nearest expiry after snapshot_date
                for exp_str in expirations:
                    exp_date = datetime.strptime(exp_str, '%Y-%m-%d').date()
                    if exp_date > snapshot_date:
                        # Get chain
                        chain = stock.option_chain(exp_str)
                        calls = chain.calls.to_dict('records')
                        puts = chain.puts.to_dict('records')
                        
                        all_opts = []
                        for opt in calls:
                            all_opts.append({
                                'ticker': ticker,
                                'expiry': exp_date,
                                'strike': opt['strike'],
                                'type': 'call',
                                'last_price': opt.get('lastPrice', 0),
                                'bid': opt.get('bid', 0),
                                'ask': opt.get('ask', 0),
                                'volume': opt.get('volume', 0),
                                'open_interest': opt.get('openInterest', 0),
                                'implied_volatility': opt.get('impliedVolatility', 0.3),
                            })
                        for opt in puts:
                            all_opts.append({
                                'ticker': ticker,
                                'expiry': exp_date,
                                'strike': opt['strike'],
                                'type': 'put',
                                'last_price': opt.get('lastPrice', 0),
                                'bid': opt.get('bid', 0),
                                'ask': opt.get('ask', 0),
                                'volume': opt.get('volume', 0),
                                'open_interest': opt.get('openInterest', 0),
                                'implied_volatility': opt.get('impliedVolatility', 0.3),
                            })
                        
                        chains[snapshot_date] = all_opts
                        break
            
        except Exception as e:
            log.debug(f"Options fetch error: {e}")
        
        return chains
    
    async def _load_yahoo_news(
        self,
        tickers: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[MarketEvent]:
        """
        Load historical news from Yahoo Finance RSS archives.
        
        Note: Yahoo's historical news API is limited.
        This fetches recent news articles that might span the period.
        """
        events = []
        
        try:
            # Use Yahoo Finance RSS feeds filtered by ticker
            # For each ticker, scrape relevant news
            async with httpx.AsyncClient(timeout=30.0) as client:
                for ticker in tickers:
                    url = f"https://finance.yahoo.com/quote/{ticker}/news"
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    
                    response = await client.get(url, headers=headers)
                    if response.status_code == 200:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Extract news items (structure varies)
                        # This is a simplified selector
                        articles = soup.find_all('h3', limit=10)
                        
                        for article in articles:
                            title = article.get_text(strip=True)
                            link_elem = article.find_parent('a')
                            link = link_elem.get('href') if link_elem else None
                            
                            if title and link:
                                # Parse date from URL or use estimated
                                # In reality would parse article publication date
                                
                                event = MarketEvent(
                                    source=DataSource.NEWS_RSS,
                                    source_id=f"yahoo_{ticker}_{hash(title) % 10000}",
                                    title=title[:200],
                                    description=title,  # Limited without full scrape
                                    url=f"https://finance.yahoo.com{link}" if link.startswith('/') else link,
                                    published_at=datetime.utcnow(),  # Approximate
                                    raw_content=title,
                                    language="en",
                                    tags=[ticker.lower()],
                                    metadata={
                                        'ticker': ticker,
                                        'source': 'yahoo_finance',
                                    }
                                )
                                events.append(event)
        except Exception as e:
            log.debug(f"Yahoo news load failed: {e}")
        
        return events
    
    async def load_from_csv(
        self,
        filepath: str,
        ticker: str,
        date_format: str = '%Y-%m-%d'
    ) -> None:
        """
        Load price data from CSV file.
        
        CSV format:
        date,open,high,low,close,volume
        2024-01-01,100.0,102.0,99.5,101.5,1000000
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {filepath}")
        
        price_data = {}
        
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            series = []
            
            for row in reader:
                try:
                    dt = datetime.strptime(row['date'], date_format).date()
                    close = float(row['close'])
                    series.append((dt, {
                        'open': float(row.get('open', close)),
                        'high': float(row.get('high', close)),
                        'low': float(row.get('low', close)),
                        'close': close,
                        'volume': int(row.get('volume', 0)),
                    }))
                except (KeyError, ValueError) as e:
                    log.warning(f"Skipping malformed row: {e}")
                    continue
            
            price_data[ticker] = series
        
        self.repo.store_historical_data([], {}, price_data)
        log.info(f"Loaded {len(series)} price points from {filepath}")
    
    async def load_events_from_json(
        self,
        filepath: str,
        source_name: str = "json_import"
    ) -> None:
        """
        Load market events from JSON file.
        
        JSON format: array of event objects matching MarketEvent schema
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"JSON file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        events = []
        for item in data:
            try:
                event = MarketEvent(
                    source=DataSource.UNKNOWN,
                    source_id=item.get('id', str(uuid.uuid4())),
                    title=item['title'],
                    description=item.get('description', ''),
                    url=item.get('url'),
                    published_at=datetime.fromisoformat(item['published_at'].replace('Z', '+00:00')),
                    raw_content=item.get('content', item['title']),
                    language=item.get('language', 'en'),
                    tags=item.get('tags', []),
                    metadata=item.get('metadata', {}),
                )
                events.append(event)
            except Exception as e:
                log.warning(f"Failed to parse event: {e}")
                continue
        
        # Append to repository
        self.repo.store_historical_data(events, {}, {})
        log.info(f"Loaded {len(events)} events from {filepath}")


async def load_standard_market_data(
    repo: "HistoricalDataRepository",
    tickers: List[str] = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA'],
    start: datetime = None,
    end: datetime = None
) -> None:
    """
    Convenience function to load standard market data for simulations.
    
    Loads:
    - Price data for major ETFs/indexes
    - Basic news events
    - (No options chains by default - expensive)
    """
    if start is None:
        start = datetime(2023, 1, 1)
    if end is None:
        end = datetime(2024, 1, 1)
    
    loader = HistoricalDataLoader(repo, None)
    
    # Download price data from Yahoo
    await loader.load_from_yahoo(tickers, start, end, include_news=True)
    
    log.info("Standard market data loading complete")
