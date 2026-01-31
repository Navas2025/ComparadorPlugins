"""
Main application module that coordinates scraping, comparison, and notifications.
"""
import logging
import threading
from datetime import datetime

from .scraper import WeadownScraper, PluginswpScraper
from .comparator import PluginComparator
from .email_notifier import EmailNotifier
from .database import Database
from .config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComparisonRunner:
    """Coordinates the comparison process."""
    
    def __init__(self):
        self.config = Config()
        self.db = Database(self.config.DATABASE_PATH)
        self.notifier = EmailNotifier(self.config)
        self.comparator = PluginComparator()
        self.weadown_scraper = WeadownScraper()
        self.pluginswp_scraper = PluginswpScraper()
        self.running = False
        self.thread = None
    
    def run_comparison(self):
        """Run the comparison process (blocking)."""
        try:
            logger.info("Starting comparison process...")
            self.running = True
            
            # Scrape both sites
            logger.info("Scraping weadown.com...")
            weadown_plugins = self.weadown_scraper.scrape_plugins()
            
            logger.info("Scraping pluginswp.online...")
            pluginswp_plugins = self.pluginswp_scraper.scrape_plugins()
            
            # Compare versions
            logger.info("Comparing plugin versions...")
            differences = self.comparator.compare(weadown_plugins, pluginswp_plugins)
            
            # Save to database
            logger.info(f"Saving {len(differences)} differences to database...")
            comparison_id = self.db.save_comparison(differences)
            
            # Send email notification if there are differences
            if differences:
                logger.info("Sending email notification...")
                try:
                    self.notifier.send_differences(differences)
                except Exception as e:
                    logger.error(f"Failed to send email: {e}")
            
            logger.info(f"Comparison complete! Found {len(differences)} differences")
            self.running = False
            
            return {
                'success': True,
                'comparison_id': comparison_id,
                'differences_count': len(differences)
            }
            
        except Exception as e:
            logger.error(f"Comparison failed: {e}")
            self.db.save_comparison([], status='error', error_message=str(e))
            self.running = False
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_comparison_async(self):
        """Run comparison in a background thread."""
        if self.running:
            logger.warning("Comparison already running")
            return False
        
        self.thread = threading.Thread(target=self.run_comparison)
        self.thread.daemon = True
        self.thread.start()
        return True
    
    def is_running(self):
        """Check if comparison is currently running."""
        return self.running
    
    def stop(self):
        """Stop the comparison process (if possible)."""
        if self.running:
            logger.info("Stopping comparison process...")
            self.running = False
            return True
        return False
