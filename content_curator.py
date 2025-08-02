import os
import re
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import hashlib
from urllib.parse import urlparse
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Article:
    """Data class to represent a news article"""
    title: str
    content: str
    url: str
    source: str
    published_date: datetime
    summary: str = ""
    relevance_score: float = 0.0
    categories: List[str] = None
    keywords: List[str] = None
    
    def __post_init__(self):
        if self.categories is None:
            self.categories = []
        if self.keywords is None:
            self.keywords = []

class ContentCuratorAgent:
    """
    Content Curator Agent for Indian Startup News Bot
    Handles article processing, summarization, and content curation
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Content Curator Agent
        
        Args:
            api_key: Optional API key for external services
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.processed_urls = set()
        self.startup_keywords = self._load_startup_keywords()
        self.indian_startup_terms = self._load_indian_terms()
        self.category_keywords = self._load_category_keywords()
        
    def _load_startup_keywords(self) -> List[str]:
        """Load startup-related keywords for relevance scoring"""
        return [
            'startup', 'startups', 'entrepreneur', 'entrepreneurship', 'venture capital',
            'vc', 'funding', 'investment', 'investor', 'seed funding', 'series a',
            'series b', 'series c', 'ipo', 'unicorn', 'decacorn', 'valuation',
            'fintech', 'edtech', 'healthtech', 'agritech', 'foodtech', 'mobility',
            'e-commerce', 'saas', 'b2b', 'b2c', 'marketplace', 'platform',
            'innovation', 'technology', 'digital', 'mobile app', 'artificial intelligence',
            'machine learning', 'blockchain', 'cryptocurrency', 'IoT', 'AR', 'VR',
            'incubator', 'accelerator', 'mentor', 'bootstrap', 'pivot', 'scale',
            'growth hacking', 'product market fit', 'mvp', 'minimum viable product'
        ]
    
    def _load_indian_terms(self) -> List[str]:
        """Load India-specific terms for relevance scoring"""
        return [
            'india', 'indian', 'mumbai', 'delhi', 'bangalore', 'bengaluru',
            'hyderabad', 'chennai', 'pune', 'kolkata', 'ahmedabad', 'surat',
            'jaipur', 'lucknow', 'kanpur', 'nagpur', 'indore', 'thane',
            'bhopal', 'visakhapatnam', 'pimpri', 'patna', 'vadodara',
            'ghaziabad', 'ludhiana', 'agra', 'nashik', 'faridabad',
            'meerut', 'rajkot', 'kalyan', 'vasai', 'varanasi', 'srinagar',
            'aurangabad', 'dhanbad', 'amritsar', 'navi mumbai', 'allahabad',
            'howrah', 'gwalior', 'jabalpur', 'coimbatore', 'vijayawada',
            'jodhpur', 'madurai', 'raipur', 'kota', 'guwahati', 'chandigarh',
            'solapur', 'hubli', 'tiruchirappalli', 'bareilly', 'mysore',
            'tiruppur', 'gurgaon', 'noida', 'bhubaneswar', 'salem',
            'mira bhayandar', 'thiruvananthapuram', 'bhiwandi', 'saharanpur',
            'gorakhpur', 'guntur', 'bikaner', 'amravati', 'noida', 'jamshedpur',
            'bhilai', 'warangal', 'cuttack', 'firozabad', 'kochi', 'bhavnagar',
            'dehradun', 'durgapur', 'asansol', 'rourkela', 'nanded', 'kolhapur',
            'ajmer', 'akola', 'gulbarga', 'jamnagar', 'ujjain', 'loni',
            'siliguri', 'jhansi', 'ulhasnagar', 'nellore', 'jammu', 'sangli miraj kupwad',
            'belgaum', 'mangalore', 'ambattur', 'tirunelveli', 'malegaon',
            'gaya', 'jalgaon', 'udaipur', 'maheshtala'
        ]
    
    def _load_category_keywords(self) -> Dict[str, List[str]]:
        """Load category-specific keywords for article classification"""
        return {
            'fintech': [
                'fintech', 'financial technology', 'payments', 'digital payments',
                'upi', 'wallet', 'neobank', 'lending', 'credit', 'insurance',
                'insurtech', 'wealthtech', 'robo advisor', 'cryptocurrency',
                'blockchain', 'digital banking', 'payment gateway', 'pos',
                'point of sale', 'merchant', 'acquirer', 'settlement'
            ],
            'edtech': [
                'edtech', 'education technology', 'e-learning', 'online learning',
                'mooc', 'lms', 'learning management', 'upskilling', 'reskilling',
                'skill development', 'test prep', 'coaching', 'tutoring',
                'educational content', 'gamification', 'adaptive learning'
            ],
            'healthtech': [
                'healthtech', 'telemedicine', 'digital health', 'health tech',
                'medical technology', 'diagnostics', 'healthcare', 'telehealth',
                'medical devices', 'pharma', 'biotechnology', 'wellness',
                'mental health', 'fitness', 'nutrition', 'medtech'
            ],
            'ecommerce': [
                'e-commerce', 'ecommerce', 'online retail', 'marketplace',
                'shopping', 'consumer', 'd2c', 'direct to consumer',
                'retail tech', 'fashion', 'beauty', 'electronics',
                'home decor', 'furniture', 'grocery', 'food delivery'
            ],
            'mobility': [
                'mobility', 'transportation', 'logistics', 'supply chain',
                'delivery', 'ride sharing', 'cab', 'taxi', 'auto',
                'bike taxi', 'electric vehicle', 'ev', 'autonomous',
                'fleet management', 'last mile', 'warehousing'
            ],
            'agritech': [
                'agritech', 'agriculture technology', 'farming', 'precision agriculture',
                'farm tech', 'rural', 'farmer', 'crop', 'livestock',
                'agricultural', 'food security', 'supply chain agriculture'
            ],
            'proptech': [
                'proptech', 'real estate', 'property', 'housing', 'rental',
                'commercial real estate', 'construction tech', 'smart city',
                'urban planning', 'facility management'
            ],
            'enterprise': [
                'enterprise', 'b2b', 'business to business', 'saas',
                'software as a service', 'erp', 'crm', 'hr tech',
                'hrtech', 'payroll', 'compliance', 'automation',
                'productivity', 'collaboration', 'workflow'
            ]
        }
    
    def process_articles(self, raw_articles: List[Dict]) -> List[Article]:
        """
        Process raw articles into Article objects with enhanced metadata
        
        Args:
            raw_articles: List of raw article dictionaries
            
        Returns:
            List of processed Article objects
        """
        processed_articles = []
        
        for raw_article in raw_articles:
            try:
                # Skip if already processed
                if raw_article.get('url') in self.processed_urls:
                    continue
                
                # Create Article object
                article = Article(
                    title=raw_article.get('title', ''),
                    content=raw_article.get('content', ''),
                    url=raw_article.get('url', ''),
                    source=raw_article.get('source', ''),
                    published_date=self._parse_date(raw_article.get('published_date'))
                )
                
                # Skip if essential fields are missing
                if not article.title or not article.content or not article.url:
                    logger.warning(f"Skipping article with missing essential fields: {article.url}")
                    continue
                
                # Calculate relevance score
                article.relevance_score = self._calculate_relevance_score(article)
                
                # Skip articles with low relevance
                if article.relevance_score < 0.3:
                    logger.info(f"Skipping low relevance article: {article.title}")
                    continue
                
                # Extract keywords
                article.keywords = self._extract_keywords(article)
                
                # Classify into categories
                article.categories = self._classify_article(article)
                
                # Generate summary
                article.summary = self._generate_summary(article)
                
                # Add to processed set
                self.processed_urls.add(article.url)
                processed_articles.append(article)
                
                logger.info(f"Processed article: {article.title}")
                
            except Exception as e:
                logger.error(f"Error processing article: {e}")
                continue
        
        return processed_articles
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string into datetime object"""
        if not date_str:
            return datetime.now()
        
        try:
            # Try different date formats
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
                '%d/%m/%Y',
                '%m/%d/%Y',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%dT%H:%M:%S'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # If all formats fail, return current time
            logger.warning(f"Could not parse date: {date_str}")
            return datetime.now()
            
        except Exception as e:
            logger.error(f"Error parsing date {date_str}: {e}")
            return datetime.now()
    
    def _calculate_relevance_score(self, article: Article) -> float:
        """
        Calculate relevance score for an article based on startup and India keywords
        
        Args:
            article: Article object
            
        Returns:
            Relevance score between 0 and 1
        """
        text = f"{article.title} {article.content}".lower()
        
        # Count startup keywords
        startup_score = 0
        for keyword in self.startup_keywords:
            if keyword.lower() in text:
                startup_score += text.count(keyword.lower())
        
        # Count Indian terms
        india_score = 0
        for term in self.indian_startup_terms:
            if term.lower() in text:
                india_score += text.count(term.lower())
        
        # Normalize scores
        max_startup_score = len(self.startup_keywords) * 3  # Assume max 3 occurrences per keyword
        max_india_score = len(self.indian_startup_terms) * 2  # Assume max 2 occurrences per term
        
        normalized_startup = min(startup_score / max_startup_score, 1.0) if max_startup_score > 0 else 0
        normalized_india = min(india_score / max_india_score, 1.0) if max_india_score > 0 else 0
        
        # Weighted combination (70% startup relevance, 30% India relevance)
        final_score = (normalized_startup * 0.7) + (normalized_india * 0.3)
        
        return min(final_score, 1.0)
    
    def _extract_keywords(self, article: Article) -> List[str]:
        """
        Extract relevant keywords from article
        
        Args:
            article: Article object
            
        Returns:
            List of extracted keywords
        """
        text = f"{article.title} {article.content}".lower()
        keywords = []
        
        # Extract startup keywords
        for keyword in self.startup_keywords:
            if keyword.lower() in text:
                keywords.append(keyword)
        
        # Extract Indian location keywords
        for term in self.indian_startup_terms:
            if term.lower() in text:
                keywords.append(term)
        
        # Remove duplicates and return
        return list(set(keywords))
    
    def _classify_article(self, article: Article) -> List[str]:
        """
        Classify article into categories based on content
        
        Args:
            article: Article object
            
        Returns:
            List of category names
        """
        text = f"{article.title} {article.content}".lower()
        categories = []
        
        for category, keywords in self.category_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text:
                    score += text.count(keyword.lower())
            
            # If score is above threshold, add category
            if score >= 2:  # At least 2 keyword matches
                categories.append(category)
        
        return categories if categories else ['general']
    
    def _generate_summary(self, article: Article) -> str:
        """
        Generate a summary of the article
        
        Args:
            article: Article object
            
        Returns:
            Article summary
        """
        try:
            # Simple extractive summarization
            sentences = self._split_into_sentences(article.content)
            
            if len(sentences) <= 3:
                return article.content
            
            # Score sentences based on keyword frequency
            sentence_scores = {}
            for i, sentence in enumerate(sentences):
                score = 0
                sentence_lower = sentence.lower()
                
                # Score based on startup keywords
                for keyword in self.startup_keywords:
                    if keyword.lower() in sentence_lower:
                        score += 2
                
                # Score based on Indian terms
                for term in self.indian_startup_terms:
                    if term.lower() in sentence_lower:
                        score += 1
                
                # Bonus for first few sentences
                if i < 3:
                    score += 3 - i
                
                sentence_scores[i] = score
            
            # Select top 3 sentences
            top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:3]
            top_sentences = sorted(top_sentences, key=lambda x: x[0])  # Sort by original order
            
            summary_sentences = [sentences[i] for i, _ in top_sentences]
            return ' '.join(summary_sentences)
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            # Fallback to first 200 characters
            return article.content[:200] + "..." if len(article.content) > 200 else article.content
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def filter_articles_by_date(self, articles: List[Article], days: int = 7) -> List[Article]:
        """
        Filter articles by date range
        
        Args:
            articles: List of Article objects
            days: Number of days to look back
            
        Returns:
            Filtered list of articles
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        return [article for article in articles if article.published_date >= cutoff_date]
    
    def rank_articles(self, articles: List[Article]) -> List[Article]:
        """
        Rank articles by relevance score and recency
        
        Args:
            articles: List of Article objects
            
        Returns:
            Ranked list of articles
        """
        def ranking_score(article):
            # Combine relevance score with recency
            days_old = (datetime.now() - article.published_date).days
            recency_score = max(0, 1 - (days_old / 30))  # Decay over 30 days
            
            return (article.relevance_score * 0.7) + (recency_score * 0.3)
        
        return sorted(articles, key=ranking_score, reverse=True)
    
    def get_trending_keywords(self, articles: List[Article], limit: int = 10) -> List[Tuple[str, int]]:
        """
        Get trending keywords from recent articles
        
        Args:
            articles: List of Article objects
            limit: Number of keywords to return
            
        Returns:
            List of (keyword, frequency) tuples
        """
        keyword_counts = {}
        
        for article in articles:
            for keyword in article.keywords:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        # Sort by frequency and return top keywords
        trending = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        return trending[:limit]
    
    def get_articles_by_category(self, articles: List[Article], category: str) -> List[Article]:
        """
        Filter articles by category
        
        Args:
            articles: List of Article objects
            category: Category name
            
        Returns:
            Filtered list of articles
        """
        return [article for article in articles if category.lower() in [cat.lower() for cat in article.categories]]
    
    def generate_content_report(self, articles: List[Article]) -> Dict:
        """
        Generate a comprehensive content report
        
        Args:
            articles: List of Article objects
            
        Returns:
            Content report dictionary
        """
        if not articles:
            return {"error": "No articles to analyze"}
        
        # Calculate basic stats
        total_articles = len(articles)
        avg_relevance = sum(article.relevance_score for article in articles) / total_articles
        
        # Category distribution
        category_counts = {}
        for article in articles:
            for category in article.categories:
                category_counts[category] = category_counts.get(category, 0) + 1
        
        # Source distribution
        source_counts = {}
        for article in articles:
            source_counts[article.source] = source_counts.get(article.source, 0) + 1
        
        # Trending keywords
        trending_keywords = self.get_trending_keywords(articles)
        
        # Date range
        dates = [article.published_date for article in articles]
        date_range = {
            'earliest': min(dates).isoformat() if dates else None,
            'latest': max(dates).isoformat() if dates else None
        }
        
        return {
            'total_articles': total_articles,
            'average_relevance_score': round(avg_relevance, 3),
            'category_distribution': category_counts,
            'source_distribution': source_counts,
            'trending_keywords': trending_keywords,
            'date_range': date_range,
            'top_articles': [
                {
                    'title': article.title,
                    'url': article.url,
                    'relevance_score': article.relevance_score,
                    'categories': article.categories
                }
                for article in self.rank_articles(articles)[:5]
            ]
        }
    
    def save_articles_to_json(self, articles: List[Article], filename: str) -> bool:
        """
        Save articles to JSON file
        
        Args:
            articles: List of Article objects
            filename: Output filename
            
        Returns:
            Success status
        """
        try:
            articles_data = []
            for article in articles:
                articles_data.append({
                    'title': article.title,
                    'content': article.content,
                    'url': article.url,
                    'source': article.source,
                    'published_date': article.published_date.isoformat(),
                    'summary': article.summary,
                    'relevance_score': article.relevance_score,
                    'categories': article.categories,
                    'keywords': article.keywords
                })
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(articles_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(articles)} articles to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving articles to JSON: {e}")
            return False
    
    def load_articles_from_json(self, filename: str) -> List[Article]:
        """
        Load articles from JSON file
        
        Args:
            filename: Input filename
            
        Returns:
            List of Article objects
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                articles_data = json.load(f)
            
            articles = []
            for data in articles_data:
                article = Article(
                    title=data['title'],
                    content=data['content'],
                    url=data['url'],
                    source=data['source'],
                    published_date=datetime.fromisoformat(data['published_date']),
                    summary=data.get('summary', ''),
                    relevance_score=data.get('relevance_score', 0.0),
                    categories=data.get('categories', []),
                    keywords=data.get('keywords', [])
                )
                articles.append(article)
            
            logger.info(f"Loaded {len(articles)} articles from {filename}")
            return articles
            
        except Exception as e:
            logger.error(f"Error loading articles from JSON: {e}")
            return []

# Example usage and testing
if __name__ == "__main__":
    # Initialize the curator
    curator = ContentCuratorAgent()
    
    # Example raw articles data
    sample_articles = [
        {
            'title': 'Indian Fintech Startup Raises $50M Series B',
            'content': 'A Bangalore-based fintech startup focused on digital payments has raised $50 million in Series B funding. The startup plans to expand its services across India and enhance its payment gateway technology.',
            'url': 'https://example.com/article1',
            'source': 'TechCrunch India',
            'published_date': '2024-01-15 10:30:00'
        },
        {
            'title': 'New EdTech Platform Launches in Mumbai',
            'content': 'An innovative education technology platform has launched in Mumbai, offering AI-powered learning solutions for students. The platform uses machine learning to provide personalized learning experiences.',
            'url': 'https://example.com/article2',
            'source': 'The Economic Times',
            'published_date': '2024-01-14 14:20:00'
        }
    ]
    
    # Process articles
    processed_articles = curator.process_articles(sample_articles)
    
    # Generate report
    report = curator.generate_content_report(processed_articles)
    print("Content Report:")
    print(json.dumps(report, indent=2))
    
    # Save to file
    curator.save_articles_to_json(processed_articles, 'processed_articles.json')
