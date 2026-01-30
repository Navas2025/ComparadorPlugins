"""
Configuration module for the Plugin Comparator application.
Loads environment variables from .env file.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration from environment variables."""
    
    # SMTP Configuration
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    SMTP_FROM = os.getenv('SMTP_FROM', '')
    SMTP_TO = os.getenv('SMTP_TO', '')
    
    # Application Configuration
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    DATABASE_PATH = os.getenv('DATABASE_PATH', './data/comparisons.db')
    SCHEDULE_ENABLED = os.getenv('SCHEDULE_ENABLED', 'true').lower() == 'true'
    SCHEDULE_HOUR = int(os.getenv('SCHEDULE_HOUR', 9))
    SCHEDULE_MINUTE = int(os.getenv('SCHEDULE_MINUTE', 0))
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        errors = []
        
        if not cls.SMTP_HOST:
            errors.append("SMTP_HOST is required")
        if not cls.SMTP_USERNAME:
            errors.append("SMTP_USERNAME is required")
        if not cls.SMTP_PASSWORD:
            errors.append("SMTP_PASSWORD is required")
        if not cls.SMTP_FROM:
            errors.append("SMTP_FROM is required")
        if not cls.SMTP_TO:
            errors.append("SMTP_TO is required")
            
        return errors
    
    @classmethod
    def is_configured(cls):
        """Check if SMTP is properly configured."""
        return all([
            cls.SMTP_HOST,
            cls.SMTP_USERNAME,
            cls.SMTP_PASSWORD,
            cls.SMTP_FROM,
            cls.SMTP_TO
        ])
