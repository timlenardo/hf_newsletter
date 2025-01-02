import os
from datetime import datetime
from pathlib import Path
from postmarker.core import PostmarkClient
from dotenv import load_dotenv
from huggingface_hub import HfApi
from database import Database

from email_template import get_email_template

def fetch_trending_projects(db):
    api = HfApi()
    
    # Fetch top models by downloads
    popular_models = api.list_models(
        sort="downloads",
        direction=-1,
        limit=500,  # Look at top 500 models
        full=True
    )
    
    # Convert generator to list for processing
    all_models = list(popular_models)
    
    trending_projects = []
    for model in all_models:
        # Calculate growth metrics
        metrics = db.calculate_growth_metrics(
            model.modelId,
            model.lastModified,
            model.likes,
            getattr(model, 'downloads', 0)
        )
        
        # Check if model is worth featuring
        if db.is_model_worth_featuring(metrics):
            try:
                # Get the model description from Hugging Face
                model_info = api.model_info(model.modelId)
                card_data = getattr(model_info, 'cardData', {}) or {}
                description = card_data.get('model-description', "No description available")
                
                # Format growth metrics for display
                growth_info = []
                if metrics['is_new']:
                    growth_info.append("🆕 New to Top 500")
                else:
                    days = max(1, metrics['days_since_update'])
                    weeks = max(1, days / 7)
                    
                    if metrics['likes_growth']:
                        weekly_growth = (metrics['likes_growth'] / weeks) * 100
                        if weekly_growth > 25:  # Show if more than 25% weekly growth
                            growth_info.append(f"⭐ {weekly_growth:.0f}% likes/week")
                    
                    if metrics['downloads_growth']:
                        weekly_growth = (metrics['downloads_growth'] / weeks) * 100
                        if weekly_growth > 50:  # Show if more than 50% weekly growth
                            growth_info.append(f"📈 {weekly_growth:.0f}% downloads/week")
                
                growth_text = " | ".join(growth_info) if growth_info else ""
                
            except Exception as e:
                print(f"Error processing {model.modelId}: {str(e)}")
                description = "No description available"
                growth_text = ""
            
            project_data = {
                'title': model.modelId,
                'author': model.author,
                'description': description,
                'growth': growth_text,
                'likes': f"{model.likes} ❤️",
                'link': f"https://huggingface.co/{model.modelId}",
                'tags': getattr(model, 'tags', []),
                'downloads': getattr(model, 'downloads', 0),
                'last_modified': model.lastModified,
                # Additional data for database
                'model_id': model.modelId,
                'likes_count': model.likes
            }
            trending_projects.append(project_data)
            
            # Update database
            db.update_highlighted_model({
                'model_id': model.modelId,
                'author': model.author,
                'last_modified': model.lastModified,
                'likes': model.likes,
                'downloads': getattr(model, 'downloads', 0)
            })
    
    return trending_projects[:10]  # Return top 10 trending projects

def create_email_content(projects):
    return get_email_template(projects)

def send_email(recipient_email, html_content):
    load_dotenv()
    
    postmark_token = os.getenv('POSTMARK_TOKEN')
    if not postmark_token:
        raise ValueError("POSTMARK_TOKEN not found in environment variables")
    
    sender_email = os.getenv('SENDER_EMAIL', 'newsletter@openhands.dev')
    
    if not recipient_email:
        recipient_email = os.getenv('RECIPIENT_EMAIL')
        if not recipient_email:
            raise ValueError("No recipient email provided")
    
    # Initialize Postmark client
    postmark = PostmarkClient(server_token=postmark_token)
    
    # Send email using Postmark
    response = postmark.emails.send(
        From=sender_email,
        To=recipient_email,
        Subject='🤗 Rising Stars in Hugging Face Top 500',
        HtmlBody=html_content,
        MessageStream='outbound'  # Default stream
    )
    
    return response