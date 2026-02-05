"""
Scraper module for extracting plugin/theme data from websites.
"""
import re
import requests
from bs4 import BeautifulSoup
import time
import logging
import unicodedata
import json
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseScraper:
    """Base scraper class with common functionality."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def _extract_version(self, text):
        """Extract version number from text."""
        if not text:
            return None
        
        # Look for version patterns like v1.2.3, 1.2.3, version 1.2
        patterns = [
            r'v?(\d+\.\d+(?:\.\d+)?(?:\.\d+)?)',  # Matches 1.2, 1.2.3, 1.2.3.4
            r'version\s+(\d+\.\d+(?:\.\d+)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _clean_plugin_name(self, title):
        """Extract clean plugin name from title."""
        if not title:
            return None
        
        # Normalize unicode characters
        title = unicodedata.normalize('NFKD', title)
        
        # Remove version numbers first
        name = re.sub(r'v?\d+\.\d+(?:\.\d+)?(?:\.\d+)?', '', title)
        
        # Remove common suffixes (at word boundaries)
        name = re.sub(r'\b(pro|premium|nulled|free|download|wordpress|plugin|theme|version)\b', '', name, flags=re.IGNORECASE)
        
        # Remove everything after " - " or "|"
        name = re.sub(r'\s+[\-–|]\s+.*$', '', name)
        
        # Clean up extra punctuation and whitespace
        name = name.strip(' -–|:')
        
        # Convert to lowercase and normalize whitespace
        name = ' '.join(name.lower().split())
        
        return name if name else None


class WeadownScraper(BaseScraper):
    """Scraper for weadown.com with pagination support."""
    
    BASE_URL = "https://weadown.com"
    
    def _build_page_url(self, page_number):
        """Construct URL for specific page - override in subclass for different categories."""
        path_prefix = "/wordpress-plugins/"
        if page_number == 1:
            return f"{self.BASE_URL}{path_prefix}"
        return f"{self.BASE_URL}{path_prefix}page/{page_number}/"
    
    def scrape_plugins(self, max_pages=5):
        """
        Scrape plugin/theme information from weadown.com with pagination.
        Returns a dict mapping plugin names to their version and download URL.
        
        Args:
            max_pages: Maximum number of pages to scrape (default: 5)
        """
        plugins = {}
        
        for page_num in range(1, max_pages + 1):
            try:
                url = self._build_page_url(page_num)
                
                logger.info(f"Scraping page {page_num}: {url}")
                
                response = self.session.get(url, timeout=30)
                
                # Stop if page doesn't exist
                if response.status_code == 404:
                    logger.info(f"No more pages found at page {page_num}")
                    break
                
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract articles using improved detection
                articles = self._locate_article_elements(soup)
                
                if not articles:
                    logger.warning(f"No articles found on page {page_num}")
                    break
                
                logger.info(f"Found {len(articles)} entries on page {page_num}")
                page_plugins = 0
                
                for article in articles:
                    try:
                        # Extract title - check new HTML structure first
                        title_elem = self._find_title_element(article)
                        
                        if not title_elem:
                            continue
                        
                        # Get the link (usually the title is wrapped in <a>)
                        link_elem = title_elem.find('a') if title_elem.find('a') else article.find('a', href=re.compile(r'/\d{4}/'))
                        
                        title = title_elem.get_text(strip=True)
                        
                        # Get post URL (not the direct download)
                        post_url = None
                        if link_elem and 'href' in link_elem.attrs:
                            post_url = link_elem['href']
                            if not post_url.startswith('http'):
                                post_url = self.BASE_URL + post_url
                        
                        # Extract version from title
                        version = self._extract_version(title)
                        
                        # Extract clean plugin name
                        plugin_name = self._clean_plugin_name(title)
                        
                        if plugin_name and post_url:
                            # Store with post URL (download URL would require visiting each post)
                            plugins[plugin_name] = {
                                'version': version,
                                'download_url': post_url,  # This is the post URL
                                'raw_title': title,
                                'source': 'weadown'
                            }
                            page_plugins += 1
                    
                    except Exception as e:
                        logger.debug(f"Error parsing article: {e}")
                        continue
                
                logger.info(f"Extracted {page_plugins} plugins from page {page_num}")
                
                # Add delay between pages to be respectful
                if page_num < max_pages:
                    time.sleep(1)
            
            except requests.exceptions.RequestException as e:
                logger.error(f"Error scraping page {page_num}: {e}")
                break
            except Exception as e:
                logger.error(f"Unexpected error on page {page_num}: {e}")
                break
        
        logger.info(f"Total scraped: {len(plugins)} plugins from weadown.com")
        return plugins
    
    def _locate_article_elements(self, soup):
        """Find article containers - checks for tdb-title-text structure first."""
        # New structure: look for h1.tdb-title-text and get parent
        h1_titles = soup.find_all('h1', class_='tdb-title-text')
        if h1_titles:
            parents = []
            for h1 in h1_titles:
                parent_article = h1.find_parent('article') or h1.find_parent('div', class_=re.compile(r'post'))
                if parent_article and parent_article not in parents:
                    parents.append(parent_article)
            if parents:
                return parents
        
        # Fallback to standard selectors
        found = soup.find_all('article', class_=re.compile(r'post'))
        if found:
            return found
        found = soup.find_all('div', class_='post-item')
        if found:
            return found
        return soup.find_all('article')
    
    def _find_title_element(self, container):
        """Extract title element, prioritizing tdb-title-text."""
        # Check new structure
        tdb_title = container.find('h1', class_='tdb-title-text')
        if tdb_title:
            return tdb_title
        # Fallback
        elem = container.find(['h2', 'h3', 'h4'], class_=re.compile(r'(entry-title|post-title|title)'))
        if elem:
            return elem
        return container.find(['h1', 'h2', 'h3', 'h4'])


class PluginswpScraper(BaseScraper):
    """Scraper for plugins-wp.online with JetEngine load-more support."""
    
    BASE_URL = "https://plugins-wp.online"
    
    def _get_category_endpoint(self):
        """Return the category path - override for themes."""
        return "/plugins-wordpress/"
    
    def scrape_plugins(self, max_pages=5):
        """
        Scrape plugin/theme information from plugins-wp.online.
        Handles JetEngine load-more AJAX pagination.
        
        Args:
            max_pages: Maximum number of pages to load (default: 5)
        
        Returns:
            dict: Mapping plugin names to their version and metadata
        """
        plugins = {}
        
        try:
            # First, load the initial page to get the structure and any AJAX endpoints
            url = f"{self.BASE_URL}{self._get_category_endpoint()}"
            logger.info(f"Scraping {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for JetEngine load-more button/AJAX configuration
            # JetEngine typically uses data attributes like data-query, data-page, etc.
            load_more_button = soup.find('div', class_=re.compile(r'jet-listing-grid__load-more'))
            
            if not load_more_button:
                load_more_button = soup.find('button', class_=re.compile(r'load-more'))
            
            # Try to find JetEngine AJAX settings
            ajax_config = None
            scripts = soup.find_all('script')
            for script in scripts:
                script_text = script.string if script.string else ''
                # Look for JetEngine config in JavaScript
                if 'jet-engine' in script_text or 'listingData' in script_text:
                    # Try to extract AJAX configuration
                    match = re.search(r'listingData["\']?\s*:\s*(\{[^}]+\})', script_text)
                    if match:
                        try:
                            ajax_config = json.loads(match.group(1))
                        except json.JSONDecodeError as e:
                            logger.debug(f"Failed to parse AJAX config: {e}")
                            pass
            
            # Extract plugins from current page
            page_plugins = self._extract_plugins_from_page(soup)
            plugins.update(page_plugins)
            logger.info(f"Extracted {len(page_plugins)} plugins from initial page")
            
            # Try to load more pages if requested
            # Note: JetEngine AJAX detection is present but falls back to standard pagination
            if max_pages > 1:
                plugins.update(self._load_more_pages_standard(max_pages))
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error scraping pluginswp.online: {e}")
        except Exception as e:
            logger.error(f"Unexpected error scraping pluginswp.online: {e}")
            logger.debug(traceback.format_exc())
        
        logger.info(f"Total scraped: {len(plugins)} plugins from pluginswp.online")
        return plugins
    
    def _extract_plugins_from_page(self, soup):
        """Extract plugins from a BeautifulSoup page object."""
        plugins = {}
        
        # Find plugin entries - try multiple selectors
        # JetEngine often uses jet-listing-grid__items
        container = soup.find('div', class_=re.compile(r'jet-listing-grid__items'))
        
        if container:
            articles = container.find_all('div', class_=re.compile(r'jet-listing-grid__item'))
        else:
            # Fallback to standard article tags
            articles = soup.find_all('article')
        
        if not articles:
            articles = soup.find_all('div', class_='post')
        
        logger.debug(f"Found {len(articles)} potential plugin entries")
        
        for article in articles:
            try:
                # Extract title - try multiple selectors
                title_elem = article.find(['h2', 'h3', 'h4'], class_=re.compile(r'(entry-title|post-title|title|jet-listing-dynamic-field)'))
                if not title_elem:
                    title_elem = article.find(['h2', 'h3', 'h4'])
                
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                
                # Extract version - check title first, then elementor structure
                version = self._extract_version(title)
                if not version:
                    version = self._scan_elementor_version_info(article)
                
                # Try to find post URL
                link_elem = title_elem.find('a') if title_elem.find('a') else article.find('a')
                post_url = None
                if link_elem and 'href' in link_elem.attrs:
                    post_url = link_elem['href']
                    if post_url and not post_url.startswith('http'):
                        post_url = self.BASE_URL + post_url
                
                # Extract clean plugin name
                plugin_name = self._clean_plugin_name(title)
                
                if plugin_name:
                    plugins[plugin_name] = {
                        'version': version,
                        'post_url': post_url,
                        'raw_title': title,
                        'source': 'pluginswp'
                    }
            
            except Exception as e:
                logger.debug(f"Error parsing article: {e}")
                continue
        
        return plugins
    
    def _scan_elementor_version_info(self, container):
        """Look for version in elementor icon list spans."""
        icon_texts = container.find_all('span', class_='elementor-icon-list-text')
        for span_elem in icon_texts:
            content = span_elem.get_text(strip=True)
            # Match Spanish/English "Version actual:" pattern
            if 'versión actual:' in content.lower() or 'version actual:' in content.lower():
                ver_match = re.search(r'actual:\s*v?(\d+\.\d+(?:\.\d+)?)', content, re.IGNORECASE)
                if ver_match:
                    return ver_match.group(1)
        return None
    
    def _load_more_pages_standard(self, max_pages):
        """Load additional pages using standard pagination."""
        plugins = {}
        category_path = self._get_category_endpoint()
        
        for page_num in range(2, max_pages + 1):
            try:
                # Try common pagination patterns with category
                urls_to_try = [
                    f"{self.BASE_URL}{category_path}page/{page_num}/",
                    f"{self.BASE_URL}{category_path}?paged={page_num}",
                ]
                
                success = False
                for url in urls_to_try:
                    try:
                        logger.info(f"Trying page {page_num}: {url}")
                        response = self.session.get(url, timeout=30)
                        
                        if response.status_code == 404:
                            continue
                        
                        response.raise_for_status()
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        page_plugins = self._extract_plugins_from_page(soup)
                        
                        if page_plugins:
                            plugins.update(page_plugins)
                            logger.info(f"Extracted {len(page_plugins)} plugins from page {page_num}")
                            success = True
                            break
                    
                    except requests.exceptions.RequestException:
                        continue
                
                if not success:
                    logger.info(f"No more pages found at page {page_num}")
                    break
                
                # Delay between pages
                time.sleep(1)
            
            except Exception as e:
                logger.error(f"Error loading page {page_num}: {e}")
                break
        
        return plugins


class ThemeScraperForWeadown(WeadownScraper):
    """Specialized scraper for Weadown theme listings."""
    
    def _build_page_url(self, page_number):
        """Override to use theme category."""
        theme_path = "/wordpress-theme/"
        if page_number == 1:
            return f"{self.BASE_URL}{theme_path}"
        return f"{self.BASE_URL}{theme_path}page/{page_number}/"


class ThemeScraperForPluginsWp(PluginswpScraper):
    """Specialized scraper for Plugins-WP theme listings."""
    
    def _get_category_endpoint(self):
        """Override to use theme category."""
        return "/temas-wordpress/"

