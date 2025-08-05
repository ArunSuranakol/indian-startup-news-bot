#!/usr/bin/env python3
"""
Carousel Designer AI Agent
Creates professional LinkedIn carousel slides for startup news
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager
import numpy as np
from datetime import datetime
import textwrap
import os

class CarouselDesignerAgent:
    """AI Agent responsible for creating LinkedIn carousel slides"""
    
    def __init__(self):
        """Initialize the carousel designer with brand guidelines"""
        
        # LinkedIn carousel specifications
        self.slide_size = (10.8, 10.8)  # 1080x1080px at 100 DPI
        self.dpi = 100
        
        # Brand color palette (professional startup theme)
        self.colors = {
            'primary': '#1e3a8a',      # Deep blue
            'secondary': '#3b82f6',    # Medium blue  
            'accent': '#f59e0b',       # Orange/amber
            'success': '#10b981',      # Green
            'text_primary': '#1f2937', # Dark gray
            'text_secondary': '#6b7280', # Medium gray
            'text_light': '#9ca3af',   # Light gray
            'background': '#ffffff',   # White
            'card_bg': '#f8fafc',      # Very light gray
            'border': '#e5e7eb'        # Light border
        }
        
        # Typography settings
        self.fonts = {
            'title': {'size': 24, 'weight': 'bold'},
            'headline': {'size': 18, 'weight': 'bold'},
            'body': {'size': 14, 'weight': 'normal'},
            'caption': {'size': 12, 'weight': 'normal'},
            'number': {'size': 32, 'weight': 'bold'}
        }
        
        # Set matplotlib to use a clean font
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
    
    def create_carousel(self, top_stories):
        """Main method to create complete carousel"""
        print(f"🎨 Creating LinkedIn carousel with {len(top_stories) + 1} slides...")
        
        slides = []
        
        try:
            # Create title slide
            print("📝 Creating title slide...")
            title_slide = self._create_title_slide()
            slides.append(title_slide)
            
            # Create individual story slides
            for i, story in enumerate(top_stories, 1):
                print(f"📰 Creating slide {i}: {story['title'][:50]}...")
                story_slide = self._create_story_slide(i, story)
                slides.append(story_slide)
            
            print(f"✅ Successfully created {len(slides)} carousel slides")
            return slides
            
        except Exception as e:
            print(f"❌ Error creating carousel: {str(e)}")
            # Return at least a title slide
            return slides if slides else [self._create_error_slide()]
    
    def _create_title_slide(self):
        """Create the main title slide"""
        fig, ax = plt.subplots(figsize=self.slide_size, dpi=self.dpi)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Background gradient effect
        gradient = np.linspace(0, 1, 256).reshape(256, -1)
        gradient = np.vstack((gradient, gradient))
        ax.imshow(gradient, extent=[0, 1, 0, 1], aspect='auto', 
                 cmap='Blues', alpha=0.1)
        
        # Main background
        background = patches.Rectangle((0, 0), 1, 1, 
                                     facecolor=self.colors['primary'],
                                     edgecolor='none')
        ax.add_patch(background)
        
        # Decorative elements
        # Top accent bar
        accent_bar = patches.Rectangle((0, 0.95), 1, 0.05,
                                     facecolor=self.colors['accent'],
                                     edgecolor='none')
        ax.add_patch(accent_bar)
        
        # Rocket emoji and main title
        ax.text(0.5, 0.75, '🚀', ha='center', va='center', 
                fontsize=60, color='white')
        
        ax.text(0.5, 0.6, 'TOP 10', ha='center', va='center',
                fontsize=48, color='white', weight='bold')
        
        ax.text(0.5, 0.48, 'INDIAN STARTUP', ha='center', va='center',
                fontsize=28, color='white', weight='bold')
        
        ax.text(0.5, 0.4, 'NEWS DIGEST', ha='center', va='center',
                fontsize=28, color='white', weight='bold')
        
        # Date
        today = datetime.now().strftime('%B %d, %Y')
        ax.text(0.5, 0.25, today, ha='center', va='center',
                fontsize=20, color=self.colors['accent'], weight='bold')
        
        # Subtitle
        ax.text(0.5, 0.15, 'Curated by AI • Ready for LinkedIn', 
                ha='center', va='center',
                fontsize=16, color='white', alpha=0.9)
        
        # Bottom decorative line
        ax.plot([0.2, 0.8], [0.08, 0.08], color=self.colors['accent'], 
                linewidth=3)
        
        # Save slide
        filename = 'slide_00_title.png'
        plt.tight_layout()
        plt.savefig(filename, dpi=self.dpi, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        return filename
    
    def _create_story_slide(self, rank, story):
        """Create individual story slide"""
        fig, ax = plt.subplots(figsize=self.slide_size, dpi=self.dpi)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Background
        background = patches.Rectangle((0, 0), 1, 1,
                                     facecolor=self.colors['background'],
                                     edgecolor='none')
        ax.add_patch(background)
        
        # Header bar
        header = patches.Rectangle((0, 0.9), 1, 0.1,
                                 facecolor=self.colors['primary'],
                                 edgecolor='none')
        ax.add_patch(header)
        
        # Rank number circle
        circle = patches.Circle((0.12, 0.82), 0.08,
                              facecolor=self.colors['accent'],
                              edgecolor='white', linewidth=3)
        ax.add_patch(circle)
        
        ax.text(0.12, 0.82, f'{rank}', ha='center', va='center',
                fontsize=self.fonts['number']['size'], 
                color='white', weight='bold')
        
        # "Top Stories" text in header
        ax.text(0.95, 0.95, 'INDIAN STARTUP NEWS', 
                ha='right', va='center',
                fontsize=14, color='white', weight='bold')
        
        # Main content card
        card = patches.Rectangle((0.05, 0.15), 0.9, 0.6,
                               facecolor=self.colors['card_bg'],
                               edgecolor=self.colors['border'],
                               linewidth=2, alpha=0.8)
        ax.add_patch(card)
        
        # Story title (wrapped)
        title_wrapped = self._wrap_text(story['title'], 35)
        ax.text(0.5, 0.65, title_wrapped, ha='center', va='center',
                fontsize=self.fonts['headline']['size'],
                color=self.colors['text_primary'],
                weight='bold', linespacing=1.3)
        
        # Story summary (wrapped)
        summary_text = story['summary'][:250] + '...' if len(story['summary']) > 250 else story['summary']
        summary_wrapped = self._wrap_text(summary_text, 45)
        
        ax.text(0.5, 0.4, summary_wrapped, ha='center', va='center',
                fontsize=self.fonts['body']['size'],
                color=self.colors['text_secondary'],
                linespacing=1.4)
        
        # Source and importance indicator
        ax.text(0.5, 0.22, f"📰 {story['source']}", 
                ha='center', va='center',
                fontsize=self.fonts['caption']['size'],
                color=self.colors['text_light'])
        
        # Importance score visualization
        score = min(story.get('importance_score', 5), 10)
        self._add_importance_indicator(ax, score)
        
        # Footer
        footer_text = f"Slide {rank} of 10 • {datetime.now().strftime('%Y')}"
        ax.text(0.5, 0.05, footer_text, ha='center', va='center'
