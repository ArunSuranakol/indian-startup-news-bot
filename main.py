#!/usr/bin/env python3
# Updated: Force fresh workflow run
#!/usr/bin/env python3
"""
Indian Startup News AI Agent System
Main orchestrator that coordinates all agents
"""

import os
import sys
from datetime import datetime
import traceback

# Import our AI agents
from news_collector import NewsCollectorAgent
from content_curator import ContentCuratorAgent
from carousel_designer import CarouselDesignerAgent
from email_sender import EmailSenderAgent

def main():
    """Main function that orchestrates all AI agents"""
    print(f"🚀 Starting Indian Startup News AI Agent System")
    print(f"⏰ Execution time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
    print("-" * 60)
    
    try:
        # Initialize all AI agents
        print("🤖 Initializing AI agents...")
        collector = NewsCollectorAgent()
        curator = ContentCuratorAgent()
        designer = CarouselDesignerAgent()
        emailer = EmailSenderAgent()
        print("✅ All agents initialized successfully")
        
        # Step 1: Collect news from various sources
        print("\n📰 Agent 1: Collecting news from Indian startup sources...")
        articles = collector.collect_daily_news()
        print(f"✅ Collected {len(articles)} startup-related articles")
        
        if len(articles) == 0:
            print("❌ No articles found. Exiting...")
            return
        
        # Step 2: AI curation to select top 10 stories
        print("\n🧠 Agent 2: AI curating top stories...")
        top_stories = curator.curate_top_stories(articles)
        print(f"✅ Selected top {len(top_stories)} most important stories")
        
        # Step 3: Generate LinkedIn carousel slides
        print("\n🎨 Agent 3: Creating LinkedIn carousel slides...")
        carousel_slides = designer.create_carousel(top_stories)
        print(f"✅ Generated {len(carousel_slides)} professional carousel slides")
        
        # Step 4: Send email with carousel and links
        print("\n📧 Agent 4: Sending email with carousel and news links...")
        emailer.send_daily_digest(carousel_slides, top_stories)
        print("✅ Email sent successfully!")
        
        print("\n" + "=" * 60)
        print("🎉 Daily Indian Startup News digest completed successfully!")
        print("📱 Check your email for LinkedIn carousel images and news links")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error in main process: {str(e)}")
        print("📋 Full error details:")
        traceback.print_exc()
        
        # Try to send error notification
        try:
            emailer = EmailSenderAgent()
            emailer.send_error_notification(str(e))
            print("📧 Error notification sent to email")
        except:
            print("❌ Could not send error notification")
        
        sys.exit(1)

if __name__ == "__main__":
    main()
