#!/usr/bin/env python3
"""
Email Sender AI Agent
Sends daily startup news digest with LinkedIn carousel and clickable links
"""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime
import base64

class EmailSenderAgent:
    """AI Agent responsible for sending daily news digest emails"""
    
    def __init__(self):
        """Initialize email sender with Gmail SMTP configuration"""
        
        # Gmail SMTP settings (free)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
        # Get credentials from environment variables (GitHub secrets)
        self.sender_email = os.getenv('SENDER_EMAIL', 'your-email@gmail.com')
        self.sender_password = os.getenv('GMAIL_APP_PASSWORD', '')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL', self.sender_email)
        
        # Email templates
        self.subject_templates = [
            "🚀 Your Daily Indian Startup Brief - {date}",
            "📰 Top 10 Startup Stories You Can't Miss - {date}",
            "🇮🇳 Indian Startup Ecosystem Update - {date}",
            "💼 Daily Startup News Digest - {date}"
        ]
    
    def send_daily_digest(self, carousel_slides, top_stories):
        """Main method to send daily digest email"""
        try:
            print(f"📧 Preparing email with {len(carousel_slides)} slides and {len(top_stories)} stories...")
            
            # Create email message
            msg = self._create_email_message(carousel_slides, top_stories)
            
            # Send email
            self._send_email(msg)
            print("✅ Daily digest email sent successfully!")
            
        except Exception as e:
            print(f"❌ Error sending email: {str(e)}")
            raise e
    
    def _create_email_message(self, carousel_slides, top_stories):
        """Create the complete email message"""
        # Create multipart message
        msg = MIMEMultipart('related')
        
        # Email headers
        today = datetime.now().strftime('%B %d, %Y')
        subject = self.subject_templates[0].format(date=today)
        
        msg['From'] = self.sender_email
        msg['To'] = self.recipient_email
        msg['Subject'] = subject
        
        # Create HTML body
        html_body = self._create_html_body(top_stories, len(carousel_slides))
        msg.attach(MIMEText(html_body, 'html'))
        
        # Attach carousel images
        self._attach_carousel_images(msg, carousel_slides)
        
        return msg
    
    def _create_html_body(self, stories, slide_count):
        """Create HTML email body"""
        today = datetime.now().strftime('%B %d, %Y')
        
        # Create carousel preview section
        carousel_html = self._create_carousel_html(slide_count)
        
        # Create stories list
        stories_html = self._create_stories_html(stories)
        
        # Main HTML template
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Indian Startup News Digest</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    background-color: #f8fafc;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background-color: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: bold;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    font-size: 16px;
                    opacity: 0.9;
                }}
                .content {{
                    padding: 30px;
                }}
                .section {{
                    margin-bottom: 40px;
                }}
                .section h2 {{
                    color: #1e3a8a;
                    font-size: 22px;
                    margin-bottom: 20px;
                    padding-bottom: 10px;
                    border-bottom: 2px solid #f59e0b;
                }}
                .carousel-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin-bottom: 20px;
                }}
                .carousel-item {{
                    text-align: center;
                    padding: 10px;
                    background-color: #f8fafc;
                    border-radius: 8px;
                    border: 1px solid #e5e7eb;
                }}
                .carousel-item img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 6px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }}
                .stories-list {{
                    list-style: none;
                    padding: 0;
                }}
                .story-item {{
                    background-color: #f8fafc;
                    margin-bottom: 20px;
                    padding: 20px;
                    border-radius: 10px;
                    border-left: 4px solid #f59e0b;
                    transition: transform 0.2s ease;
                }}
                .story-item:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                }}
                .story-title {{
                    font-size: 18px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .story-title a {{
                    color: #1e3a8a;
                    text-decoration: none;
                }}
                .story-title a:hover {{
                    color: #3b82f6;
                    text-decoration: underline;
                }}
                .story-summary {{
                    color: #6b7280;
                    font-size: 14px;
                    margin-bottom: 10px;
                    line-height: 1.5;
                }}
                .story-meta {{
                    font-size: 12px;
                    color: #9ca3af;
                    font-style: italic;
                }}
                .download-instructions {{
                    background-color: #dbeafe;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    border: 1px solid #3b82f6;
                }}
                .footer {{
                    background-color: #1f2937;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                }}
                .footer a {{
                    color: #f59e0b;
                    text-decoration: none;
                }}
                .rank-badge {{
                    display: inline-block;
                    background-color: #f59e0b;
                    color: white;
                    padding: 4px 8px;
                    border-radius: 15px;
                    font-size: 12px;
                    font-weight: bold;
                    margin-right: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Indian Startup News Digest</h1>
                    <p>Top 10 Stories • {today} • Curated by AI</p>
                </div>
                
                <div class="content">
                    <div class="section">
                        <h2>📱 LinkedIn Carousel Images</h2>
                        <div class="download-instructions">
                            <strong>📋 How to use:</strong>
                            <ol>
                                <li>Right-click on each image below and select "Save image as..."</li>
                                <li>Save all images to your computer</li>
                                <li>Go to LinkedIn and create a new post</li>
                                <li>Upload all images in order (they'll create a carousel automatically)</li>
                                Add your caption and post!</li>
    </ol>
</div>
"""
