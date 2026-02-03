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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeadownScraper:
    """Scraper for weadown.com with pagination support."""
    
    BASE_URL = "https://weadown.com"
    MAX_PAGES = 10  # Maximum number of pages to scrape
    
    # Common regex patterns for version extraction
    VERSION_PATTERNS = [
        r'v?(\d+\.\d+(?:\.\d+)?(?:\.\d+)?)',  # Support up to 4 parts
        r'version\s+(\d+\.\d+(?:\.\d+)?(?:\.\d+)?)',
        r'ver\s+(\d+\.\d+(?:\.\d+)?(?:\.\d+)?)',
    ]
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_plugins(self):
        """
        Scrape plugin/theme information from weadown.com with pagination.
        Crawls through paginated lists and extracts post links, titles, and versions.
        Returns a dict mapping plugin names to their version and download URL.
        """
        plugins = {}
        page_num = 0  # Initialize to track pages scraped
        
        try:
            # Scrape multiple pages of WordPress plugins
            for page_num in range(1, self.MAX_PAGES + 1):
                if page_num == 1:
                    url = f"{self.BASE_URL}/category/wordpress-plugins/"
                else:
                    url = f"{self.BASE_URL}/category/wordpress-plugins/page/{page_num}/"
                
                logger.info(f"Scraping page {page_num}: {url}")
                
                try:
                    response = self.session.get(url, timeout=30)
                    response.raise_for_status()
                except requests.RequestException as e:
                    logger.warning(f"Failed to fetch page {page_num}: {e}")
                    # If we fail on page 1, it's an error; otherwise, we've reached the end
                    if page_num == 1:
                        raise
                    break
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find plugin entries - try multiple selectors
                articles = soup.find_all('article', class_='post')
                
                if not articles:
                    # Try alternative selectors
                    articles = soup.find_all('div', class_='post-item')
                
                if not articles:
                    # Try more generic article tags
                    articles = soup.find_all('article')
                
                if not articles:
                    logger.info(f"No articles found on page {page_num}, stopping pagination")
                    break
                
                logger.info(f"Found {len(articles)} potential plugin entries on page {page_num}")
                
                page_had_results = False
                for article in articles:
                    try:
                        # Try to extract plugin name and version
                        title_elem = article.find(['h2', 'h3', 'h4'])
                        if not title_elem:
                            continue
                        
                        # Get the post link
                        link_elem = title_elem.find('a')
                        if not link_elem and title_elem.parent.name == 'a':
                            link_elem = title_elem.parent
                        elif not link_elem:
                            link_elem = article.find('a')
                        
                        # Extract title text
                        title = title_elem.get_text(strip=True)
                        
                        # Try to find version in title or content
                        version = self._extract_version(title)
                        
                        # Get post/download URL
                        post_url = link_elem.get('href') if link_elem else None
                        
                        if post_url and not post_url.startswith('http'):
                            post_url = self.BASE_URL + post_url
                        
                        # Extract clean plugin name
                        plugin_name = self._clean_plugin_name(title)
                        
                        if plugin_name and post_url:
                            plugins[plugin_name] = {
                                'version': version,
                                'download_url': post_url,
                                'raw_title': title
                            }
                            page_had_results = True
                    
                    except Exception as e:
                        logger.debug(f"Error parsing article: {e}")
                        continue
                
                # If we didn't find any valid results on this page, stop
                if not page_had_results:
                    logger.info(f"No valid results on page {page_num}, stopping pagination")
                    break
                
                # Add a small delay between page requests to be polite
                time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Error scraping weadown.com: {e}")
        
        logger.info(f"Scraped {len(plugins)} plugins from weadown.com across {page_num} page(s)")
        return plugins
    
    def _extract_version(self, text):
        """Extract version number from text."""
        # Normalize the text using unicodedata
        text = unicodedata.normalize('NFKD', text)
        
        # Use class-level patterns
        for pattern in self.VERSION_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    @staticmethod
    def _clean_plugin_name(title):
        """Extract clean plugin name from title using unicodedata for normalization."""
        # Normalize unicode characters
        title = unicodedata.normalize('NFKD', title)
        
        # Remove version numbers and common suffixes
        name = re.sub(r'v?\d+\.\d+(?:\.\d+)?(?:\.\d+)?', '', title, flags=re.IGNORECASE)
        name = re.sub(r'\s+(pro|premium|nulled|free|download|latest|update)\s*', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*[\[\(].*?[\]\)]', '', name)  # Remove bracketed content
        name = name.strip(' -–|:,.')
        
        # Convert to lowercase and strip extra whitespace
        name = ' '.join(name.lower().split())
        return name if name else None


class PluginswpScraper:
    """Scraper for pluginswp.online with JetEngine AJAX load-more support."""
    
    BASE_URL = "http://pluginswp.online"
    MAX_LOADS = 10  # Maximum number of AJAX load-more requests
    
    # Shared regex patterns for version extraction
    VERSION_PATTERNS = WeadownScraper.VERSION_PATTERNS
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'X-Requested-With': 'XMLHttpRequest',  # For AJAX requests
        })
    
    def scrape_plugins(self):
        """
        Scrape plugin/theme information from pluginswp.online.
        Handles JetEngine load-more flow for dynamic content loading.
        Returns a dict mapping plugin names to their version.
        """
        plugins = {}
        
        try:
            # Load the main page first
            url = self.BASE_URL
            logger.info(f"Scraping {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse initial page content
            self._parse_page_content(soup, plugins)
            
            # Look for JetEngine load-more parameters
            # JetEngine typically uses data attributes or scripts to configure AJAX loading
            load_more_button = soup.find('div', class_='jet-load-more') or \
                             soup.find('button', class_='jet-load-more-button') or \
                             soup.find('a', class_='jet-load-more')
            
            if load_more_button:
                logger.info("Found JetEngine load-more button, attempting AJAX loads")
                self._handle_jetengine_loadmore(load_more_button, plugins)
            else:
                # If no load-more, try pagination
                logger.info("No load-more found, trying pagination")
                self._handle_pagination(soup, plugins)
            
        except Exception as e:
            logger.error(f"Error scraping pluginswp.online: {e}")
        
        logger.info(f"Scraped {len(plugins)} plugins from pluginswp.online")
        return plugins
    
    def _parse_page_content(self, soup, plugins):
        """Parse content from a page and add to plugins dict."""
        # Find plugin entries - try multiple selectors
        articles = soup.find_all('article')
        
        if not articles:
            # Try alternative selectors
            articles = soup.find_all('div', class_='post') or \
                      soup.find_all('div', class_='jet-listing-grid__item') or \
                      soup.find_all('div', class_='elementor-post')
        
        initial_count = len(plugins)
        logger.info(f"Found {len(articles)} potential plugin entries on this load")
        
        for article in articles:
            try:
                # Try to extract plugin name and version
                title_elem = article.find(['h2', 'h3', 'h4', 'h5'])
                if not title_elem:
                    continue
                
                # Get the post link
                link_elem = title_elem.find('a')
                if not link_elem and title_elem.parent.name == 'a':
                    link_elem = title_elem.parent
                elif not link_elem:
                    link_elem = article.find('a')
                
                # Extract title text
                title = title_elem.get_text(strip=True)
                
                # Try to find version in title or content
                version = self._extract_version(title)
                
                # Get post URL
                post_url = link_elem.get('href') if link_elem else None
                
                if post_url and not post_url.startswith('http'):
                    post_url = self.BASE_URL + post_url
                
                # Extract clean plugin name
                plugin_name = self._clean_plugin_name(title)
                
                if plugin_name:
                    # Only add if not already present (avoid duplicates from AJAX loads)
                    if plugin_name not in plugins:
                        plugins[plugin_name] = {
                            'version': version,
                            'post_url': post_url,
                            'raw_title': title
                        }
            
            except Exception as e:
                logger.debug(f"Error parsing article: {e}")
                continue
        
        logger.info(f"Added {len(plugins) - initial_count} new plugins from this load")
    
    def _handle_jetengine_loadmore(self, load_more_element, plugins):
        """Handle JetEngine AJAX load-more requests."""
        try:
            # Try to extract data attributes from the load-more element
            page = 1
            
            for load_num in range(self.MAX_LOADS):
                page += 1
                
                # Try to construct AJAX request
                # JetEngine typically uses wp-admin/admin-ajax.php
                ajax_url = f"{self.BASE_URL}/wp-admin/admin-ajax.php"
                
                # Common JetEngine parameters
                data = {
                    'action': 'jet_engine_ajax',
                    'handler': 'get_listing',
                    'page': page,
                    'listing_id': load_more_element.get('data-listing-id', ''),
                    'widget_id': load_more_element.get('data-widget-id', ''),
                }
                
                # Only make request if we have necessary parameters
                if not data['listing_id'] and not data['widget_id']:
                    logger.info("Could not extract JetEngine parameters, stopping AJAX loads")
                    break
                
                logger.info(f"Attempting JetEngine AJAX load {load_num + 1} (page {page})")
                
                try:
                    response = self.session.post(ajax_url, data=data, timeout=30)
                    response.raise_for_status()
                    
                    # Try to parse JSON response
                    try:
                        json_response = response.json()
                        
                        # JetEngine typically returns HTML in 'data' field
                        if 'data' in json_response and 'html' in json_response['data']:
                            html_content = json_response['data']['html']
                        elif 'html' in json_response:
                            html_content = json_response['html']
                        else:
                            html_content = response.text
                    except json.JSONDecodeError:
                        html_content = response.text
                    
                    if not html_content or html_content.strip() == '':
                        logger.info(f"Empty response on load {load_num + 1}, stopping")
                        break
                    
                    # Parse the loaded HTML
                    ajax_soup = BeautifulSoup(html_content, 'html.parser')
                    initial_count = len(plugins)
                    self._parse_page_content(ajax_soup, plugins)
                    
                    # If no new plugins were added, stop
                    if len(plugins) == initial_count:
                        logger.info(f"No new plugins on load {load_num + 1}, stopping")
                        break
                    
                    # Add a small delay between requests
                    time.sleep(0.5)
                    
                except requests.RequestException as e:
                    logger.warning(f"AJAX request failed on load {load_num + 1}: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Error handling JetEngine load-more: {e}")
    
    def _handle_pagination(self, initial_soup, plugins):
        """Handle standard pagination if load-more is not available."""
        try:
            # Look for pagination links
            pagination = initial_soup.find(['nav', 'div'], class_=re.compile(r'pagination|paging'))
            
            if not pagination:
                logger.info("No pagination found")
                return
            
            # Find all page links
            page_links = pagination.find_all('a', href=True)
            
            # Extract page URLs
            page_urls = []
            for link in page_links:
                href = link.get('href', '')
                if href and href not in page_urls and 'page' in href.lower():
                    if not href.startswith('http'):
                        href = self.BASE_URL + href
                    page_urls.append(href)
            
            logger.info(f"Found {len(page_urls)} pagination URLs")
            
            # Scrape each page (limit to prevent excessive requests)
            for i, page_url in enumerate(page_urls[:self.MAX_LOADS], start=2):
                logger.info(f"Scraping pagination page {i}: {page_url}")
                
                try:
                    response = self.session.get(page_url, timeout=30)
                    response.raise_for_status()
                    
                    page_soup = BeautifulSoup(response.content, 'html.parser')
                    initial_count = len(plugins)
                    self._parse_page_content(page_soup, plugins)
                    
                    # If no new plugins were added, stop
                    if len(plugins) == initial_count:
                        logger.info(f"No new plugins on page {i}, stopping")
                        break
                    
                    # Add a small delay between requests
                    time.sleep(0.5)
                    
                except requests.RequestException as e:
                    logger.warning(f"Failed to fetch page {i}: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Error handling pagination: {e}")
    
    def _extract_version(self, text):
        """Extract version number from text."""
        # Normalize the text using unicodedata
        text = unicodedata.normalize('NFKD', text)
        
        # Use class-level patterns
        for pattern in self.VERSION_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    # Reuse the same name cleaning method from WeadownScraper
    _clean_plugin_name = staticmethod(WeadownScraper._clean_plugin_name)
