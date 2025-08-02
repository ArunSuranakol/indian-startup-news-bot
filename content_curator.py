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
        
        # Try to use different AI backends (fallback approach)
        self.ai_available = self._check_ai_availability()
    
    def curate_top_stories(self, articles, target_count=10):
        """Main method to curate and rank stories"""
        print(f"🧠 Starting AI curation of {len(articles)} articles...")
        
        if len(articles) == 0:
            return []
        
        # Step 1: Calculate base scores using keyword analysis
        print("📊 Calculating relevance scores...")
        scored_articles = self._calculate_base_scores(articles)
        
        # Step 2: Use AI to refine scores if available
        if self.ai_available:
            print("🤖 Enhancing scores with AI analysis...")
            scored_articles = self._ai_enhance_scores(scored_articles)
        else:
            print("📋 Using rule-based scoring (AI not available)")
        
        # Step 3: Apply recency boost
        scored_articles = self._apply_recency_boost(scored_articles)
        
        # Step 4: Ensure diversity in selection
        final_selection = self._ensure_diversity(scored_articles, target_count)
        
        # Step 5: Generate summaries
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
    
    def _check_ai_availability(self):
        """Check if AI services are available"""
        try:
            # Try Ollama first (local AI)
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and 'llama' in result.stdout:
                print("✅ Ollama AI available")
                return 'ollama'
        except:
            pass
        
        # Try Hugging Face Transformers (if available)
        try:
            import transformers
            print("✅ Hugging Face Transformers available")
            return 'huggingface'
        except ImportError:
            pass
        
        print("ℹ️  No AI backend available, using rule-based scoring")
        return False
    
    def _ai_enhance_scores(self, articles):
        """Use AI to enhance importance scores"""
        if self.ai_available == 'ollama':
            return self._ollama_enhance_scores(articles)
        elif self.ai_available == 'huggingface':
            return self._huggingface_enhance_scores(articles)
        else:
            return articles
    
    def _ollama_enhance_scores(self, articles):
        """Use Ollama to enhance scores"""
        enhanced_articles = []
        
        for article in articles[:20]:  # Limit to prevent timeout
            try:
                prompt = f"""
Rate this Indian startup news importance from 1-10:

Title: {article['title']}
Summary: {article['summary'][:300]}

Consider:
- Funding amount and stage
- Company significance 
- Market impact
- Innovation level

Respond with only a number 1-10:
"""
                
                result = subprocess.run([
                    'ollama', 'generate', 'llama2', 
                    '--prompt', prompt
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    ai_score = self._extract_number(result.stdout)
                    if ai_score:
                        # Combine rule-based and AI scores
                        article['importance_score'] = (
                            article['importance_score'] * 0.7 + ai_score * 3
                        )
                
                enhanced_articles.append(article)
                
            except Exception as e:
                print(f"⚠️  AI scoring failed for article: {str(e)}")
                enhanced_articles.append(article)
        
        # Add remaining articles without AI enhancement
        enhanced_articles.extend(articles[20:])
        return enhanced_articles
    
    def _huggingface_enhance_scores(self, articles):
        """Use Hugging Face models to enhance scores"""
        try:
            from transformers import pipeline
            
            # Use sentiment analysis as a proxy for importance
            classifier = pipeline("sentiment-analysis")
            
            for article in articles[:15]:  # Limit processing
                try:
                    text = article['title'] + ' ' + article['summary'][:200]
                    result = classifier(text)
                    
                    # Boost score for positive sentiment (usually good news)
                    if result[0]['label'] == 'POSITIVE':
                        article['importance_score'] += result[0]['score'] * 2
                        
                except Exception as e:
                    print(f"⚠️  HF scoring failed: {str(e)}")
                    continue
        
        except Exception as e:
            print(f"⚠️  HuggingFace not properly available: {str(e)}")
        
        return articles
    
    def _extract_number(self, text):
        """Extract a number from AI response"""
        try:
            # Look for numbers in the response
            numbers = re.findall(r'\b([1-9]|10)\b', text)
            if numbers:
                return int(numbers[0])
        except:
            pass
        return None
    
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
        sources_used = set()
        keywords_used = set()
        
        # First pass: select high-scoring diverse articles
        for article in articles:
            if len(selected) >= target_count:
                break
            
            source = article['source']
            content_words = set(article['title'].lower().split())
            
            # Check for diversity
            source_limit_reached = sources_used.count(source) >= 3
            too_similar = len(content_words & keywords_used) > 2
            
            if not source_limit_reached and not too_similar:
                selected.append(article)
                sources_used.add(source)
                keywords_used.update(content_words)
        
        # Second pass: fill remaining slots with best remaining articles
        remaining_slots = target_count - len(selected)
        if remaining_slots > 0:
            remaining_articles = [a for a in articles if a not in selected]
            selected.extend(remaining_articles[:remaining_slots])
        
        return selected[:target_count]
    
    def _generate_summaries(self, articles):
