"""
Test script to verify scraper functionality and HTML parsing.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.scraper import WeadownScraper, PluginswpScraper, ThemeScraperForWeadown, ThemeScraperForPluginsWp
from src.scraper_coordinator import ScraperCoordinator

def test_url_configuration():
    """Test that URLs are configured correctly."""
    print("Testing URL Configuration...")
    
    # Test WeadownScraper
    ws = WeadownScraper()
    url = ws._build_page_url(1)
    assert url == "https://weadown.com/wordpress-plugins/", f"Expected plugins URL, got {url}"
    url2 = ws._build_page_url(2)
    assert url2 == "https://weadown.com/wordpress-plugins/page/2/", f"Expected page 2 URL, got {url2}"
    
    # Test ThemeScraperForWeadown
    ts = ThemeScraperForWeadown()
    url = ts._build_page_url(1)
    assert url == "https://weadown.com/wordpress-theme/", f"Expected themes URL, got {url}"
    
    # Test PluginswpScraper
    ps = PluginswpScraper()
    assert ps.BASE_URL == "https://plugins-wp.online", f"Expected https URL, got {ps.BASE_URL}"
    assert ps._get_category_endpoint() == "/plugins-wordpress/", f"Expected plugins path, got {ps._get_category_endpoint()}"
    
    # Test ThemeScraperForPluginsWp
    tps = ThemeScraperForPluginsWp()
    assert tps._get_category_endpoint() == "/temas-wordpress/", f"Expected temas path, got {tps._get_category_endpoint()}"
    
    print("✓ URL configuration tests passed!")

def test_coordinator():
    """Test the ScraperCoordinator functionality."""
    print("\nTesting ScraperCoordinator...")
    
    coordinator = ScraperCoordinator(worker_pool_size=2)
    
    # Register tasks
    coordinator.register_task('test_wd', WeadownScraper, 1)
    coordinator.register_task('test_pw', PluginswpScraper, 1)
    
    # Check initial status
    status = coordinator.get_all_status()
    assert 'test_wd' in status, "Task not registered"
    assert status['test_wd']['state'] == 'pending', "Initial state should be pending"
    
    coordinator.shutdown()
    print("✓ Coordinator tests passed!")

def test_version_extraction():
    """Test version extraction patterns."""
    print("\nTesting Version Extraction...")
    
    from src.scraper import BaseScraper
    
    scraper = BaseScraper()
    
    # Test various version formats
    test_cases = [
        ("Plugin Name 1.2.3", "1.2.3"),
        ("Plugin v2.5.0", "2.5.0"),
        ("Something 10.11.12", "10.11.12"),
        ("version 3.4", "3.4"),
    ]
    
    for text, expected in test_cases:
        result = scraper._extract_version(text)
        assert result == expected, f"Expected {expected} from '{text}', got {result}"
    
    print("✓ Version extraction tests passed!")

def test_name_cleaning():
    """Test plugin name cleaning."""
    print("\nTesting Name Cleaning...")
    
    from src.scraper import BaseScraper
    
    scraper = BaseScraper()
    
    test_cases = [
        ("Plugin Name Pro 1.2.3", "name"),  # "plugin" and "pro" are removed
        ("Something Premium | Download", "something"),
        ("Test Plugin - WordPress", "test"),
    ]
    
    for text, expected in test_cases:
        result = scraper._clean_plugin_name(text)
        assert expected in result, f"Expected '{expected}' in cleaned name from '{text}', got '{result}'"
    
    print("✓ Name cleaning tests passed!")

if __name__ == "__main__":
    print("=" * 60)
    print("Running Scraper Tests")
    print("=" * 60)
    
    try:
        test_url_configuration()
        test_coordinator()
        test_version_extraction()
        test_name_cleaning()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed successfully!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
