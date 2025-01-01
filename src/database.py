import sqlite3
from datetime import datetime
from pathlib import Path

class Database:
    def __init__(self, db_path="newsletter.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS highlighted_models (
                    model_id TEXT PRIMARY KEY,
                    author TEXT,
                    last_highlighted TIMESTAMP,
                    last_modified TIMESTAMP,
                    likes INTEGER,
                    downloads INTEGER
                )
            ''')
            conn.commit()
    
    def get_highlighted_model(self, model_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM highlighted_models WHERE model_id = ?",
                (model_id,)
            )
            return cursor.fetchone()
    
    def update_highlighted_model(self, model_data):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO highlighted_models 
                (model_id, author, last_highlighted, last_modified, likes, downloads)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                model_data['model_id'],
                model_data['author'],
                datetime.now().isoformat(),
                model_data['last_modified'],
                model_data['likes'],
                model_data['downloads']
            ))
            conn.commit()
    
    def calculate_growth_metrics(self, model_id, last_modified, likes, downloads):
        """Calculate growth metrics for a model."""
        previous = self.get_highlighted_model(model_id)
        
        if not previous:
            return {
                'is_new': True,
                'likes_growth': None,
                'downloads_growth': None,
                'days_since_update': 0,
                'previous_record': None
            }
        
        # Calculate time-based metrics
        prev_modified = datetime.fromisoformat(previous[3])
        if isinstance(last_modified, str):
            curr_modified = datetime.fromisoformat(last_modified.replace('Z', '+00:00'))
        else:
            curr_modified = last_modified
        
        days_since_update = (curr_modified - prev_modified).days
        
        # Calculate growth metrics
        prev_likes = previous[4]
        prev_downloads = previous[5]
        
        likes_growth = ((likes - prev_likes) / prev_likes) if prev_likes > 0 else float('inf')
        downloads_growth = ((downloads - prev_downloads) / prev_downloads) if prev_downloads > 0 else float('inf')
        
        return {
            'is_new': False,
            'likes_growth': likes_growth,
            'downloads_growth': downloads_growth,
            'days_since_update': days_since_update,
            'previous_record': previous
        }
    
    def is_model_worth_featuring(self, metrics, min_likes=100):
        """Determine if a model is worth featuring based on growth metrics."""
        if metrics['is_new']:
            # For new models in top 500, they're already significant
            return True
        
        # Skip if we featured it very recently (within 14 days)
        if metrics['days_since_update'] < 14:
            return False
        
        # For established models, we want significant growth over time
        if metrics['previous_record']:
            days_since_update = max(1, metrics['days_since_update'])
            
            # Calculate weekly growth rates instead of daily
            weeks = max(1, days_since_update / 7)
            
            if metrics['likes_growth'] is not None:
                weekly_likes_growth = metrics['likes_growth'] / weeks
            else:
                weekly_likes_growth = 0
                
            if metrics['downloads_growth'] is not None:
                weekly_downloads_growth = metrics['downloads_growth'] / weeks
            else:
                weekly_downloads_growth = 0
            
            # Model is worth featuring if:
            # 1. Very high weekly growth in likes (>25% per week)
            # 2. Very high weekly growth in downloads (>50% per week)
            # 3. Exceptional total growth in either metric
            return (
                weekly_likes_growth > 0.25 or  # 25% weekly growth in likes
                weekly_downloads_growth > 0.50 or  # 50% weekly growth in downloads
                (metrics['likes_growth'] or 0) > 2.0 or  # 200% total growth in likes
                (metrics['downloads_growth'] or 0) > 5.0  # 500% total growth in downloads
            )
        
        return False
    
    def get_statistics(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get total number of models
            cursor.execute("SELECT COUNT(*) FROM highlighted_models")
            total_models = cursor.fetchone()[0]
            
            # Get most highlighted authors
            cursor.execute("""
                SELECT author, COUNT(*) as count 
                FROM highlighted_models 
                GROUP BY author 
                ORDER BY count DESC 
                LIMIT 5
            """)
            top_authors = cursor.fetchall()
            
            # Get most recent highlights
            cursor.execute("""
                SELECT model_id, author, last_highlighted 
                FROM highlighted_models 
                ORDER BY last_highlighted DESC 
                LIMIT 5
            """)
            recent_highlights = cursor.fetchall()
            
            # Get models with most likes
            cursor.execute("""
                SELECT model_id, author, likes 
                FROM highlighted_models 
                ORDER BY likes DESC 
                LIMIT 5
            """)
            most_liked = cursor.fetchall()
            
            return {
                'total_models': total_models,
                'top_authors': top_authors,
                'recent_highlights': recent_highlights,
                'most_liked': most_liked
            }
    
    def export_to_csv(self, output_path):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM highlighted_models")
            rows = cursor.fetchall()
            
            headers = ['model_id', 'author', 'last_highlighted', 
                      'last_modified', 'likes', 'downloads']
            
            with open(output_path, 'w') as f:
                f.write(','.join(headers) + '\n')
                for row in rows:
                    f.write(','.join(str(x) for x in row) + '\n')