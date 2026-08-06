
# import hashlib
# import logging
# import os
# from datetime import datetime
# from typing import Dict, List, Optional

# import bs4
# import feedparser
# import psycopg2
# import requests
# from psycopg2.extras import execute_values
# from pydantic import BaseModel

# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# # 1. Configuration
# DB_CONFIG = {
#     "dbname": "News_Events",
#     "user": "postgres",
#     "password": "12345",  # <-- Update with your DB password
#     "host": "localhost",
#     "port": "5432"
# }

# # Optional: Place your key here or set NEWS_API_KEY environment variable
# NEWS_API_KEY = os.getenv("NEWS_API_KEY", "87f90b0b7ed7425094888b4eeb9f3e01") 

# # 2. Standardized Event Model
# class RawEvent(BaseModel):
#     content_hash: str
#     source_name: str
#     title: str
#     summary: Optional[str] = None
#     raw_content: Optional[str] = None
#     source_url: str
#     published_at: Optional[str] = None


# # 3. Hybrid Ingestion Engine
# class HybridDataIngestor:
#     def __init__(self, news_api_key: Optional[str] = None):
#         self.news_api_key = news_api_key
        
#         # Background RSS Feeds (Macro & Policy scanning)
#         self.rss_sources = [
#             {
#                 "name": "BBC Business & Policy",
#                 "url": "http://feeds.bbci.co.uk/news/business/rss.xml"
#             },
#             {
#                 "name": "Economic Times (Policy)",
#                 "url": "https://economictimes.indiatimes.com/news/economy/policy/rssfeeds/13352306.cms"
#             }
#         ]
        
#         self.headers = {
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
#         }

#     @staticmethod
#     def generate_hash(url: str, title: str) -> str:
#         return hashlib.sha256(f"{url}{title}".encode('utf-8')).hexdigest()

#     @staticmethod
#     def clean_html(raw_html: str) -> str:
#         if not raw_html:
#             return ""
#         soup = bs4.BeautifulSoup(raw_html, "html.parser")
#         return soup.get_text(separator=" ", strip=True)

#     def fetch_rss_feeds(self) -> List[RawEvent]:
#         """Fetch general broad updates via background RSS feeds."""
#         events = []
#         for source in self.rss_sources:
#             logging.info(f"[RSS] Fetching from: {source['name']}")
#             try:
#                 resp = requests.get(source["url"], headers=self.headers, timeout=10)
#                 if resp.status_code != 200:
#                     logging.warning(f"HTTP {resp.status_code} for {source['name']}")
#                     continue

#                 parsed = feedparser.parse(resp.content)
#                 for entry in parsed.entries:
#                     title = entry.get("title", "").strip()
#                     link = entry.get("link", "").strip()
#                     summary = self.clean_html(entry.get("summary", entry.get("description", "")))
#                     pub_date = entry.get("published", entry.get("updated", None))

#                     if not title or not link:
#                         continue

#                     events.append(
#                         RawEvent(
#                             content_hash=self.generate_hash(link, title),
#                             source_name=source["name"],
#                             title=title,
#                             summary=summary,
#                             raw_content=summary,
#                             source_url=link,
#                             published_at=pub_date
#                         )
#                     )
#             except Exception as e:
#                 logging.error(f"Failed to ingest RSS from {source['name']}: {str(e)}")
        
#         return events

#     def fetch_company_news_api(self, company_name: str, days_back: int = 7) -> List[RawEvent]:
#         """
#         On-demand API Fetcher:
#         Queries NewsAPI for specific company policy/business news.
#         """
#         if not self.news_api_key or self.news_api_key == "YOUR_NEWS_API_KEY":
#             logging.warning("NewsAPI key not provided. Skipping API search.")
#             return []

#         logging.info(f"[API] Searching NewsAPI for targeted entity: {company_name}")
#         query = f'"{company_name}" AND (policy OR regulation OR market OR economy OR expansion)'
#         url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=en&apiKey={self.news_api_key}"
        
#         events = []
#         try:
#             response = requests.get(url, timeout=10)
#             if response.status_code == 200:
#                 data = response.json()
#                 articles = data.get("articles", [])
#                 logging.info(f"[API] Found {len(articles)} articles for '{company_name}'")
                
#                 for art in articles:
#                     title = art.get("title", "").strip()
#                     link = art.get("url", "").strip()
#                     if not title or not link:
#                         continue

#                     events.append(
#                         RawEvent(
#                             content_hash=self.generate_hash(link, title),
#                             source_name=f"NewsAPI ({art.get('source', {}).get('name', 'Unknown')})",
#                             title=title,
#                             summary=art.get("description", ""),
#                             raw_content=art.get("content", ""),
#                             source_url=link,
#                             published_at=art.get("publishedAt")
#                         )
#                     )
#             else:
#                 logging.error(f"NewsAPI error code {response.status_code}: {response.text}")
#         except Exception as e:
#             logging.error(f"NewsAPI fetch error: {str(e)}")

#         return events

#     def run_hybrid_pipeline(self, target_company: Optional[str] = None) -> List[RawEvent]:
#         all_events = []
        
#         # 1. Fetch general background policy/news from RSS
#         rss_events = self.fetch_rss_feeds()
#         all_events.extend(rss_events)

#         # 2. If a specific target company is passed, fetch targeted API data
#         if target_company:
#             api_events = self.fetch_company_news_api(target_company)
#             all_events.extend(api_events)

#         logging.info(f"Total hybrid events retrieved: {len(all_events)}")
#         return all_events


# # 4. Persistence Engine
# def save_events_to_db(events: List[RawEvent]):
#     if not events:
#         logging.info("No events to save.")
#         return

#     query = """
#         INSERT INTO raw_events (content_hash, source_name, title, summary, raw_content, source_url)
#         VALUES %s
#         ON CONFLICT (content_hash) DO NOTHING;
#     """
    
#     records = [
#         (e.content_hash, e.source_name, e.title, e.summary, e.raw_content, e.source_url)
#         for e in events
#     ]

#     try:
#         conn = psycopg2.connect(**DB_CONFIG)
#         cur = conn.cursor()
#         execute_values(cur, query, records)
#         conn.commit()
        
#         logging.info(f"Database Sync Complete! Inserted {cur.rowcount} new records.")
#         cur.close()
#         conn.close()
#     except Exception as e:
#         logging.error(f"Database error: {str(e)}")


# if __name__ == "__main__":
#     ingestor = HybridDataIngestor(news_api_key=NEWS_API_KEY)
    
#     # Test hybrid ingestion (RSS background + targeted API query for Reliance)
#     fetched_data = ingestor.run_hybrid_pipeline(target_company="Reliance Industries")
#     save_events_to_db(fetched_data)

import hashlib
import logging
import os
from typing import List, Optional

import bs4
import feedparser
import psycopg2
import requests
from dotenv import load_dotenv
from psycopg2.extras import execute_values
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Standardized Event Model
class RawEvent(BaseModel):
    content_hash: str
    source_name: str
    title: str
    summary: Optional[str] = None
    raw_content: Optional[str] = None
    source_url: str
    published_at: Optional[str] = None


# Hybrid Ingestion Engine
class HybridDataIngestor:
    def __init__(self, news_api_key: Optional[str] = None):
        self.news_api_key = news_api_key
        
        # Background RSS Feeds (Macro & Policy scanning)
        self.rss_sources = [
            {
                "name": "BBC Business & Policy",
                "url": "http://feeds.bbci.co.uk/news/business/rss.xml"
            },
            {
                "name": "Economic Times (Policy)",
                "url": "https://economictimes.indiatimes.com/news/economy/policy/rssfeeds/13352306.cms"
            }
        ]
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }

    @staticmethod
    def generate_hash(url: str, title: str) -> str:
        return hashlib.sha256(f"{url}{title}".encode('utf-8')).hexdigest()

    @staticmethod
    def clean_html(raw_html: str) -> str:
        if not raw_html:
            return ""
        soup = bs4.BeautifulSoup(raw_html, "html.parser")
        return soup.get_text(separator=" ", strip=True)

    def fetch_rss_feeds(self) -> List[RawEvent]:
        """Fetch general broad updates via background RSS feeds."""
        events = []
        for source in self.rss_sources:
            logging.info(f"[RSS] Fetching from: {source['name']}")
            try:
                resp = requests.get(source["url"], headers=self.headers, timeout=10)
                if resp.status_code != 200:
                    logging.warning(f"HTTP {resp.status_code} for {source['name']}")
                    continue

                parsed = feedparser.parse(resp.content)
                for entry in parsed.entries:
                    title = entry.get("title", "").strip()
                    link = entry.get("link", "").strip()
                    summary = self.clean_html(entry.get("summary", entry.get("description", "")))
                    pub_date = entry.get("published", entry.get("updated", None))

                    if not title or not link:
                        continue

                    events.append(
                        RawEvent(
                            content_hash=self.generate_hash(link, title),
                            source_name=source["name"],
                            title=title,
                            summary=summary,
                            raw_content=summary,
                            source_url=link,
                            published_at=pub_date
                        )
                    )
            except Exception as e:
                logging.error(f"Failed to ingest RSS from {source['name']}: {str(e)}")
        
        return events

    def fetch_company_news_api(self, company_name: str) -> List[RawEvent]:
        """Queries NewsAPI for specific company policy/business news."""
        if not self.news_api_key:
            logging.warning("NewsAPI key not provided. Skipping API search.")
            return []

        logging.info(f"[API] Searching NewsAPI for targeted entity: {company_name}")
        query = f'"{company_name}" AND (policy OR regulation OR market OR economy OR expansion)'
        url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=en&apiKey={self.news_api_key}"
        
        events = []
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                articles = data.get("articles", [])
                logging.info(f"[API] Found {len(articles)} articles for '{company_name}'")
                
                for art in articles:
                    title = art.get("title", "").strip()
                    link = art.get("url", "").strip()
                    if not title or not link:
                        continue

                    events.append(
                        RawEvent(
                            content_hash=self.generate_hash(link, title),
                            source_name=f"NewsAPI ({art.get('source', {}).get('name', 'Unknown')})",
                            title=title,
                            summary=art.get("description", ""),
                            raw_content=art.get("content", ""),
                            source_url=link,
                            published_at=art.get("publishedAt")
                        )
                    )
            else:
                logging.error(f"NewsAPI error code {response.status_code}: {response.text}")
        except Exception as e:
            logging.error(f"NewsAPI fetch error: {str(e)}")

        return events

    def run_hybrid_pipeline(self, target_company: Optional[str] = None) -> List[RawEvent]:
        all_events = []
        
        # 1. Fetch general background policy/news from RSS
        rss_events = self.fetch_rss_feeds()
        all_events.extend(rss_events)

        # 2. Fetch targeted API data if company provided
        if target_company:
            api_events = self.fetch_company_news_api(target_company)
            all_events.extend(api_events)

        logging.info(f"Total hybrid events retrieved: {len(all_events)}")
        return all_events


# Persistence Engine
def save_events_to_db(events: List[RawEvent]):
    if not events:
        logging.info("No events to save.")
        return

    if not DATABASE_URL:
        logging.error("DATABASE_URL environment variable is missing!")
        return

    query = """
        INSERT INTO raw_events (content_hash, source_name, title, summary, raw_content, source_url, published_at)
        VALUES %s
        ON CONFLICT (content_hash) DO NOTHING;
    """
    
    records = [
        (e.content_hash, e.source_name, e.title, e.summary, e.raw_content, e.source_url, e.published_at)
        for e in events
    ]

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        execute_values(cur, query, records)
        conn.commit()
        
        logging.info(f"Database Sync Complete! Inserted {cur.rowcount} new records.")
        cur.close()
        conn.close()
    except Exception as e:
        logging.error(f"Database error: {str(e)}")


if __name__ == "__main__":
    ingestor = HybridDataIngestor(news_api_key=NEWS_API_KEY)
    
    # Run pipeline for general news & specific targets
    fetched_data = ingestor.run_hybrid_pipeline(target_company="Reliance Industries")
    save_events_to_db(fetched_data)