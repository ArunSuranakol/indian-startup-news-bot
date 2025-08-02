#!/usr/bin/env python3
"""
Content Curator AI Agent
Uses AI to intelligently rank and select top startup stories
"""

import re
import subprocess
import json
from datetime import datetime
import requests
import os

class ContentCuratorAgent:
    """AI Agent responsible for curating and ranking startup news"""
    
    def __init__(self):
        """Initialize the content curator with scoring criteria"""
        
        # Scoring weights for different types of news
        self.scoring_criteria = {
            'funding_keywords': {
                'unicorn': 10, 'decacorn': 10, 'ipo': 9, 'acquisition': 8,
                'merger': 8, 'series c': 7, 'series b': 6, 'series a': 5,
                'seed': 4, 'pre-seed': 3, 'raised': 4, 'funding': 3,
                'investment': 3, 'venture capital': 4, 'valuation': 5
            },
            'amount_multipliers': {
                'billion': 8, 'crore': 3, 'million': 2, '100 crore': 6,
                '500 crore': 7, '1000 crore': 8, '$': 2, '₹': 1
            },
            'company_stage': {
                'startup': 2, 'unicorn': 10, 'public': 6, 'listed': 6,
                'enterprise': 4, 'b2b': 3, 'b2c': 3, 'd2c': 3
            },
            'sectors': {
                'fintech': 5, 'edtech': 4, 'healthtech': 5, 'foodtech': 3,
                'ecommerce': 4, 'saas': 5, 'ai': 6, 'blockchain': 4,
                'crypto': 3, 'mobility': 4, 'logistics': 4
            },
            'news_type': {
                'launched': 3, 'partnership': 4, 'expansion': 4,
                'hired': 2, 'appointed': 3, 'regulation': 5, 'policy': 5,
                'government': 4, 'international': 4, 'global': 4
            }
        }
        
        # Simple fallback scoring (no AI dependencies)
        self.ai_available = False
    
    def curate_top_stories(self, articles, target_count=10):
        """Main method to curate and rank stories"""
        print(f"🧠 Starting content curation of {len(articles)} articles...")
        
        if len(articles) == 0:
            return []
        
        # Calculate base scores using keyword analysis
        print("📊 Calculating relevance scores...")
        scored_articles = self._calculate_base_scores(articles)
        
        # Apply recency boost
        scored_articles = self._apply_recency_boost(scored_articles)
        
        # Ensure diversity in selection
        final_selection = self._ensure_diversity(scored_articles, target_count)
        
        # Generate summaries
        final_selection = self._generate_summaries(final_selection)
        
        print(f"✅ Selected top {len(final_selection)} stories")
        return final_selection
    
    def _calculate_base_scores(self, articles):
        """Calculate base importance scores using keyword analysis"""
        scored_articles = []
        
        for article in articles:
            score = 0
            content = (article['title'] + ' ' + article['summary']).lower()
            
            # Score based on funding keywords
            for keyword, weight in self.scoring_criteria['funding_keywords'].items():
                if keyword in content:
                    score += weight
            
            # Score based on amount mentioned
            for amount, multiplier in self.scoring_criteria['amount_multipliers'].items():
                if amount in content:
                    score += multiplier
            
            # Score based on company stage
            for stage, weight in self.scoring_criteria['company_stage'].items():
                if stage in content:
                    score += weight
            
            # Score based on sector
            for sector, weight in self.scoring_criteria['sectors'].items():
                if sector in content:
                    score += weight
            
            # Score based on news type
            for news_type, weight in self.scoring_criteria['news_type'].items():
                if news_type in content:
                    score += weight
            
            # Add existing relevance score from collector
            score += article.get('relevance_score', 0)
            
            article['importance_score'] = score
            scored_articles.append(article)
        
        return scored_articles
    
    def _apply_recency_boost(self, articles):
        """Apply recency boost to scores"""
        now = datetime.now()
        
        for article in articles:
            try:
                pub_time = article['published']
                hours_ago = (now - pub_time).total_seconds() / 3600
                
                # Boost recent articles
                if hours_ago < 6:
                    article['importance_score'] += 5
                elif hours_ago < 12:
                    article['importance_score'] += 3
                elif hours_ago < 24:
                    article['importance_score'] += 1
                    
            except:
                pass  # Skip if date parsing fails
        
        return articles
    
    def _ensure_diversity(self, articles, target_count):
        """Ensure diversity in source and topic selection"""
        # Sort by importance score
        articles.sort(key=lambda x: x['importance_score'], reverse=True)
        
        selected = []
        sources_used = []
        keywords_used = set()
        
        # First pass: select high-scoring diverse articles
        for article in articles:
            if len(selected) >= target_count:
                break
            
            source = article['source']
            content_words = set(article['title'].lower().split())
            
            # Check for diversity
            source_count = sources_used.count(source)
            source_limit_reached = source_count >= 3
            too_similar = len(content_words & keywords_used) > 2
            
            if not source_limit_reached and not too_similar:
                selected.append(article)
                sources_used.append(source)
                keywords_used.update(content_words)
        
        # Second pass: fill remaining slots with best remaining articles
        remaining_slots = target_count - len(selected)
        if remaining_slots > 0:
            remaining_articles = [a for a in articles if a not in selected]
            selected.extend(remaining_articles[:remaining_slots])
        
        return selected[:target_count]
    
    def _generate_summaries(self, articles):
        """Generate concise summaries for articles"""
        for article in articles:
            try:
                # Create a concise summary from title and existing summary
                title = article['title']
                summary = article['summary']
                
                # If summary is too long, truncate intelligently
                if len(summary) > 200:
                    sentences = summary.split('.')
                    condensed = sentences[0]
                    
                    # Add more sentences if there's room
                    for sentence in sentences[1:]:
                        if len(condensed + sentence) < 180:
                            condensed += '.' + sentence
                        else:
                            break
                    
                    article['summary'] = condensed.strip() + '...'
                
                # Ensure summary is not just a repeat of title
                if article['summary'].lower().startswith(title.lower()[:20]):
                    article['summary'] = summary[len(title):].strip()
                    if not article['summary']:
                        article['summary'] = "Important development in Indian startup ecosystem."
                
            except Exception as e:
                print(f"⚠️  Summary generation failed: {str(e)}")
                article['summary'] = "Significant startup news update."
        
        return articles

# Test function for standalone execution
if __name__ == "__main__":
    # Test with sample articles
    sample_articles = [
        {
            'title': 'Flipkart raises $1 billion in Series H funding',
            'summary': 'E-commerce giant Flipkart has raised $1 billion in its latest funding round, valuing the company at $37.6 billion.',
            'source': 'Economic Times',
            'published': datetime.now(),
            'relevance_score': 8
        }
    ]
    
    curator = ContentCuratorAgent()
    top_stories = curator.curate_top_stories(sample_articles)
    
    print(f"\n📊 Curation Results:")
    for i, story in enumerate(top_stories, 1):
        print(f"{i}. {story['title']}")
        print(f"   Score: {story['importance_score']:.1f}")
        print(f"   Source: {story['source']}")
        print()
