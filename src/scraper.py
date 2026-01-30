"""
Scraper module for extracting plugin/theme data from websites.
"""
import re
import requests
from bs4 import BeautifulSoup
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeadownScraper:
    """Scraper for weadown.com."""
    
    BASE_URL = "https://weadown.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_plugins(self):
        """
        Scrape plugin/theme information from weadown.com.
        Returns a dict mapping plugin names to their version and download URL.
        """
        plugins = {}
        
        try:
            # Try to get WordPress plugins page
            url = f"{self.BASE_URL}/category/wordpress-plugins/"
            logger.info(f"Scraping {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find plugin entries (this is a general approach - may need adjustment)
            articles = soup.find_all('article', class_='post')
            
            if not articles:
                # Try alternative selectors
                articles = soup.find_all('div', class_='post-item')
            
            logger.info(f"Found {len(articles)} potential plugin entries")
            
            for article in articles[:50]:  # Limit to first 50 for performance
                try:
                    # Try to extract plugin name and version
                    title_elem = article.find(['h2', 'h3', 'h4'])
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # Try to find version in title or content
                    version = self._extract_version(title)
                    
                    # Try to get download URL
                    link_elem = article.find('a')
                    download_url = link_elem['href'] if link_elem and 'href' in link_elem.attrs else None
                    
                    if download_url and not download_url.startswith('http'):
                        download_url = self.BASE_URL + download_url
                    
                    # Extract clean plugin name
                    plugin_name = self._clean_plugin_name(title)
                    
                    if plugin_name:
                        plugins[plugin_name] = {
                            'version': version,
                            'download_url': download_url,
                            'raw_title': title
                        }
                
                except Exception as e:
                    logger.debug(f"Error parsing article: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error scraping weadown.com: {e}")
        
        logger.info(f"Scraped {len(plugins)} plugins from weadown.com")
        return plugins
    
    def _extract_version(self, text):
        """Extract version number from text."""
        # Look for version patterns like v1.2.3, 1.2.3, version 1.2
        patterns = [
            r'v?(\d+\.\d+(?:\.\d+)?)',
            r'version\s+(\d+\.\d+(?:\.\d+)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _clean_plugin_name(self, title):
        """Extract clean plugin name from title."""
        # Remove version numbers and common suffixes
        name = re.sub(r'v?\d+\.\d+(?:\.\d+)?', '', title)
        name = re.sub(r'\s+(pro|premium|nulled|free|download)\s*', '', name, flags=re.IGNORECASE)
        name = name.strip(' -–|')
        return name.lower()


class PluginswpScraper:
    """Scraper for pluginswp.online."""
    
    BASE_URL = "http://pluginswp.online"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_plugins(self):
        """
        Scrape plugin/theme information from pluginswp.online.
        Returns a dict mapping plugin names to their version.
        """
        plugins = {}
        
        try:
            # Try main page or plugins category
            url = self.BASE_URL
            logger.info(f"Scraping {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find plugin entries (this is a general approach - may need adjustment)
            articles = soup.find_all('article')
            
            if not articles:
                # Try alternative selectors
                articles = soup.find_all('div', class_='post')
            
            logger.info(f"Found {len(articles)} potential plugin entries")
            
            for article in articles[:50]:  # Limit to first 50 for performance
                try:
                    # Try to extract plugin name and version
                    title_elem = article.find(['h2', 'h3', 'h4'])
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # Try to find version in title or content
                    version = self._extract_version(title)
                    
                    # Extract clean plugin name
                    plugin_name = self._clean_plugin_name(title)
                    
                    if plugin_name:
                        plugins[plugin_name] = {
                            'version': version,
                            'raw_title': title
                        }
                
                except Exception as e:
                    logger.debug(f"Error parsing article: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error scraping pluginswp.online: {e}")
        
        logger.info(f"Scraped {len(plugins)} plugins from pluginswp.online")
        return plugins
    
    def _extract_version(self, text):
        """Extract version number from text."""
        patterns = [
            r'v?(\d+\.\d+(?:\.\d+)?)',
            r'version\s+(\d+\.\d+(?:\.\d+)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _clean_plugin_name(self, title):
        """Extract clean plugin name from title."""
        # Remove version numbers and common suffixes
        name = re.sub(r'v?\d+\.\d+(?:\.\d+)?', '', title)
        name = re.sub(r'\s+(pro|premium|nulled|free|download)\s*', '', name, flags=re.IGNORECASE)
        name = name.strip(' -–|')
        return name.lower()
