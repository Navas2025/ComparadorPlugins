"""
Database module for storing comparison history.
Uses SQLite for simplicity and portability.
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path


class Database:
    """Handles all database operations for comparison history."""
    
    def __init__(self, db_path='./data/comparisons.db'):
        """Initialize database connection."""
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comparisons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_differences INTEGER NOT NULL,
                status TEXT NOT NULL,
                error_message TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS differences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                comparison_id INTEGER NOT NULL,
                plugin_name TEXT NOT NULL,
                weadown_version TEXT,
                pluginswp_version TEXT,
                download_url TEXT,
                FOREIGN KEY (comparison_id) REFERENCES comparisons(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_comparison(self, differences, status='success', error_message=None):
        """Save a comparison run and its differences."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO comparisons (timestamp, total_differences, status, error_message)
            VALUES (?, ?, ?, ?)
        ''', (timestamp, len(differences), status, error_message))
        
        comparison_id = cursor.lastrowid
        
        for diff in differences:
            cursor.execute('''
                INSERT INTO differences (comparison_id, plugin_name, weadown_version, 
                                       pluginswp_version, download_url)
                VALUES (?, ?, ?, ?, ?)
            ''', (comparison_id, diff['name'], diff.get('weadown_version'),
                  diff.get('pluginswp_version'), diff.get('download_url')))
        
        conn.commit()
        conn.close()
        
        return comparison_id
    
    def get_all_comparisons(self):
        """Retrieve all comparison runs."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, timestamp, total_differences, status, error_message
            FROM comparisons
            ORDER BY timestamp DESC
        ''')
        
        comparisons = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return comparisons
    
    def get_comparison_details(self, comparison_id):
        """Retrieve details of a specific comparison."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM comparisons WHERE id = ?
        ''', (comparison_id,))
        
        comparison = cursor.fetchone()
        if not comparison:
            conn.close()
            return None
        
        comparison = dict(comparison)
        
        cursor.execute('''
            SELECT * FROM differences WHERE comparison_id = ?
        ''', (comparison_id,))
        
        comparison['differences'] = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return comparison
    
    def get_latest_comparison(self):
        """Get the most recent comparison."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id FROM comparisons
            ORDER BY timestamp DESC
            LIMIT 1
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return self.get_comparison_details(result['id'])
        return None
