#!/usr/bin/env python3
"""
News Collector AI Agent
Collects news from various Indian startup ecosystem sources
"""

import feedparser
import requests
from datetime import datetime, timedelta
import re
from urllib.parse import urlparse
import time

class NewsCollectorAgent:
    """AI Agent responsible for collecting news from Indian startup sources"""
    
    def __init__(self):
        """Initialize the news collector with source URLs and keywords"""
        self.sources = [
            {
                'name': 'YourStory',
                'url': 'https://yourstory.com/feed',
                'type': 'rss'
            },
            {
                'name': 'Inc42',
                'url': 'https://inc42.com/feed/',
                'type': 'rss'
            },
            {
                'name': 'Economic Times Startups',
                'url': 'https://economictimes.indiatimes.com/small-biz/startups/rssfeeds/11989999.cms',
                'type': 'rss'
            },
            {
                'name': 'Business Standard Startups',
                'url': 'https://www.business-standard.com/rss/companies-104.rss',
                'type': 'rss'
            },
            {
                'name': 'VCCircle',
                'url': 'https://www.vccircle.com/feed/',
                'type': 'rss'
            }
        ]
        
        # Keywords to identify startup-related content
        self.startup_keywords = [
            'startup', 'startups', 'funding', 'investment', 'investor', 'venture capital',
            'series a', 'series b', 'series c', 'seed funding', 'pre-series',
            'unicorn', 'decacorn', 'ipo', 'initial public offering',
            'fintech', 'edtech', 'healthtech', 'foodtech', 'proptech', 'agritech',
            'saas', 'b2b', 'b2c', 'd2c', 'marketplace',
            'entrepreneur', 'entrepreneurship', 'founder', 'co-founder',
            'raised', 'valuation', 'round', 'acquisition', 'merger',
            'backed', 'led by', 'participated', 'invested'
        ]
        
        # High-priority keywords for better scoring
        self.priority_keywords = [
            'unicorn', 'ipo', 'acquisition', 'merger', 'series a', 'series b', 'series c',
            'funding', 'raised', 'crore', 'million', 'billion', 'valuation'
        ]
    
    def collect_daily_news(self):
        """Main method to collect news from all sources"""
        print(f"🔍 Starting news collection from {len(self.sources)} sources...")
        all_articles = []
        
        for source in self.sources:
            try:
                print(f"📡 Fetching from {source['name']}...")
                articles = self._fetch_from_source(source)
                filtered_articles = self._filter_startup_articles(articles, source['name'])
                all_articles.extend(filtered_articles)
                print(f"✅ Found {len(filtered_articles)} relevant articles from {source['name']}")
                
                # Be respectful - small delay between requests
                time.sleep(1)
                
            except Exception as e:
                print(f"⚠️  Error fetching from {source['name']}: {str(e)}")
                continue
        
        # Remove duplicates and sort by recency
        unique_articles = self._remove_duplicates(all_articles)
        recent_articles = self._filter_recent_articles(unique_articles)
        
        print(f"📊 Total unique recent articles: {len(recent_articles)}")
        return recent_articles
    
    def _fetch_from_source(self, source):
        """Fetch articles from a single RSS source"""
        articles = []
        
        try:
            # Set user agent to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; NewsBot/1.0)'
            }
            
            # Parse RSS feed
            feed = feedparser.parse(source['url'], request_headers=headers)
            
            if not feed.entries:
                print(f"⚠️  No entries found in {source['name']} feed")
                return articles
            
            # Extract article information
            for entry in feed.entries[:30]:  # Limit to recent 30 articles per source
                try:
                    # Clean and extract text
                    title = self._clean_text(entry.title) if hasattr(entry, 'title') else ""
                    summary = self._clean_text(entry.summary) if hasattr(entry, 'summary') else ""
                    
                    # Get publication date
                    pub_date = self._parse_date(entry)
                    
                    # Create article object
                    article = {
                        'title': title,
                        'summary': summary,
                        'url': entry.link if hasattr(entry, 'link') else "",
                        'source': source['name'],
                        'published': pub_date,
                        'raw_content': title + " " + summary
                    }
                    
                    articles.append(article)
                    
                except Exception as e:
                    print(f"⚠️  Error processing entry from {source['name']}: {str(e)}")
                    continue
        
        except Exception as e:
            print(f"❌ Failed to fetch from {source['name']}: {str(e)}")
        
        return articles
    
    def _filter_startup_articles(self, articles, source_name):
        """Filter articles to only include startup-related content"""
        filtered = []
        
        for article in articles:
            if self._is_startup_related(article['raw_content']):
                # Add relevance score for later ranking
                article['relevance_score'] = self._calculate_relevance_score(article['raw_content'])
                filtered.append(article)
        
        return filtered
    
    def _is_startup_related(self, text):
        """Check if article content is related to startups"""
        text_lower = text.lower()
        
        # Check for startup keywords
        keyword_matches = sum(1 for keyword in self.startup_keywords if keyword in text_lower)
        
        # Must have at least 2 startup-related keywords
        return keyword_matches >= 2
    
    def _calculate_relevance_score(self, text):
        """Calculate relevance score based on keyword presence"""
        text_lower = text.lower()
        score = 0
        
        # Regular keywords worth 1 point each
        for keyword in self.startup_keywords:
            if keyword in text_lower:
                score += 1
        
        # Priority keywords worth 3 points each
        for keyword in self.priority_keywords:
            if keyword in text_lower:
                score += 3
        
        return score
    
    def _clean_text(self, text):
        """Clean HTML tags and extra whitespace from text"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove common RSS artifacts
        text = re.sub(r'&[a-zA-Z]+;', '', text)
        
        return text
    
    def _parse_date(self, entry):
        """Parse publication date from RSS entry"""
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                return datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'published'):
                # Try to parse date string
                from dateutil import parser
                return parser.parse(entry.published)
            else:
                return datetime.now()
        except:
            return datetime.now()
    
    def _remove_duplicates(self, articles):
        """Remove duplicate articles based on title similarity"""
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            # Create a normalized title for comparison
            normalized_title = re.sub(r'[^\w\s]', '', article['title'].lower())
            normalized_title = re.sub(r'\s+', ' ', normalized_title).strip()
            
            if normalized_title not in seen_titles and len(normalized_title) > 10:
                seen_titles.add(normalized_title)
                unique_articles.append(article)
        
        return unique_articles
    
    def _filter_recent_articles(self, articles, hours_back=24):
        """Filter articles to only include recent ones"""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        recent_articles = []
        
        for article in articles:
            if article['published'] >= cutoff_time:
                recent_articles.append(article)
        
        # Sort by publication date (newest first)
        recent_articles.sort(key=lambda x: x['published'], reverse=True)
        
        return recent_articles

# Test function for standalone execution
if __name__ == "__main__":
    collector = NewsCollectorAgent()
    articles = collector.collect_daily_news()
    
    print(f"\n📊 Collection Results:")
    print(f"Total articles: {len(articles)}")
    
    if articles:
        print(f"\n📰 Sample articles:")
        for i, article in enumerate(articles[:3], 1):
            print(f"{i}. {article['title'][:80]}...")
            print(f"   Source: {article['source']}")
            print(f"   Score: {article['relevance_score']}")
            print()
