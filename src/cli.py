import argparse
from pathlib import Path
from datetime import datetime
import webbrowser
import tempfile

from newsletter import fetch_trending_projects, create_email_content, send_email
from database import Database
from logger import setup_logger
# web_read function is provided by the environment

def save_preview(html_content):
    """Save HTML content to a temporary file and open in browser."""
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
        f.write(html_content)
        return f.name

def display_statistics(db):
    """Display database statistics in a formatted way."""
    stats = db.get_statistics()
    
    print("\n=== Newsletter Database Statistics ===\n")
    print(f"Total models highlighted: {stats['total_models']}")
    
    print("\nTop 5 Authors:")
    for author, count in stats['top_authors']:
        print(f"  - {author}: {count} models")
    
    print("\nMost Recent Highlights:")
    for model_id, author, date in stats['recent_highlights']:
        highlight_date = datetime.fromisoformat(date).strftime('%Y-%m-%d')
        print(f"  - {model_id} by {author} ({highlight_date})")
    
    print("\nMost Liked Models:")
    for model_id, author, likes in stats['most_liked']:
        print(f"  - {model_id} by {author}: {likes} likes")

def main():
    parser = argparse.ArgumentParser(description='Hugging Face Newsletter Generator')
    parser.add_argument('--preview', action='store_true',
                      help='Generate newsletter and open in browser without sending')
    parser.add_argument('--stats', action='store_true',
                      help='Display database statistics')
    parser.add_argument('--export', type=str, metavar='PATH',
                      help='Export database to CSV file')
    parser.add_argument('--recipient', type=str,
                      help='Override recipient email from .env file')
    
    args = parser.parse_args()
    
    # Setup paths
    base_path = Path(__file__).parent.parent
    data_path = base_path / "data"
    logs_path = base_path / "logs"
    data_path.mkdir(exist_ok=True)
    
    # Setup logger
    logger = setup_logger(logs_path)
    
    # Initialize database
    db = Database(data_path / "newsletter.db")
    
    try:
        if args.stats:
            display_statistics(db)
            return
            
        if args.export:
            export_path = Path(args.export)
            db.export_to_csv(export_path)
            logger.info(f"Database exported to {export_path}")
            return
        
        # Fetch projects
        logger.info("Fetching trending projects...")
        projects = fetch_trending_projects(db)
        
        if not projects:
            logger.info("No new or updated projects found")
            return
        
        logger.info(f"Found {len(projects)} new or updated projects")
        
        # Create newsletter content
        logger.info("Creating email content...")
        html_content = create_email_content(projects)
        
        if args.preview:
            preview_path = save_preview(html_content)
            logger.info(f"Opening preview in browser...")
            webbrowser.open(f'file://{preview_path}')
            return
        
        # Send newsletter
        logger.info("Sending email...")
        recipient = args.recipient
        send_email(recipient, html_content)
        
        logger.info("Newsletter sent successfully!")
    
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()