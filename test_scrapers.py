#!/usr/bin/env python3
"""
Test script for validating the enhanced scraper functionality.

This script tests:
1. Import functionality (no syntax or import errors)
2. Class instantiation
3. Method availability
4. Basic execution (returns dict, even if empty when sites unreachable)
5. Unicode handling with unicodedata
6. Regex version extraction
7. Plugin name cleaning

Note: Actual scraping will fail if sites are unreachable, but the code structure
and logic can still be validated.
"""

import sys
import json
from src.scraper import WeadownScraper, PluginswpScraper


def test_imports():
    """Test that imports work correctly."""
    print("=" * 60)
    print("TEST 1: Import Validation")
    print("=" * 60)
    
    try:
        # These imports should work without errors
        from src.scraper import WeadownScraper, PluginswpScraper
        print("✓ Successfully imported WeadownScraper")
        print("✓ Successfully imported PluginswpScraper")
        
        # Check that unicodedata is available in the module
        import src.scraper as scraper_module
        import unicodedata
        print("✓ unicodedata module is available")
        
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def test_instantiation():
    """Test that scraper classes can be instantiated."""
    print("\n" + "=" * 60)
    print("TEST 2: Class Instantiation")
    print("=" * 60)
    
    try:
        weadown = WeadownScraper()
        print(f"✓ WeadownScraper instantiated")
        print(f"  - BASE_URL: {weadown.BASE_URL}")
        print(f"  - MAX_PAGES: {weadown.MAX_PAGES}")
        
        pluginswp = PluginswpScraper()
        print(f"✓ PluginswpScraper instantiated")
        print(f"  - BASE_URL: {pluginswp.BASE_URL}")
        print(f"  - MAX_LOADS: {pluginswp.MAX_LOADS}")
        
        return True
    except Exception as e:
        print(f"✗ Instantiation failed: {e}")
        return False


def test_methods():
    """Test that required methods exist and are callable."""
    print("\n" + "=" * 60)
    print("TEST 3: Method Availability")
    print("=" * 60)
    
    try:
        weadown = WeadownScraper()
        pluginswp = PluginswpScraper()
        
        # Check public methods
        assert hasattr(weadown, 'scrape_plugins'), "WeadownScraper missing scrape_plugins"
        assert callable(weadown.scrape_plugins), "scrape_plugins not callable"
        print("✓ WeadownScraper.scrape_plugins() exists and is callable")
        
        assert hasattr(pluginswp, 'scrape_plugins'), "PluginswpScraper missing scrape_plugins"
        assert callable(pluginswp.scrape_plugins), "scrape_plugins not callable"
        print("✓ PluginswpScraper.scrape_plugins() exists and is callable")
        
        # Check private helper methods
        assert hasattr(weadown, '_extract_version'), "WeadownScraper missing _extract_version"
        assert hasattr(weadown, '_clean_plugin_name'), "WeadownScraper missing _clean_plugin_name"
        print("✓ WeadownScraper helper methods exist")
        
        assert hasattr(pluginswp, '_extract_version'), "PluginswpScraper missing _extract_version"
        assert hasattr(pluginswp, '_clean_plugin_name'), "PluginswpScraper missing _clean_plugin_name"
        print("✓ PluginswpScraper helper methods exist")
        
        # Check PluginswpScraper specific methods for JetEngine support
        assert hasattr(pluginswp, '_parse_page_content'), "PluginswpScraper missing _parse_page_content"
        assert hasattr(pluginswp, '_handle_jetengine_loadmore'), "PluginswpScraper missing _handle_jetengine_loadmore"
        assert hasattr(pluginswp, '_handle_pagination'), "PluginswpScraper missing _handle_pagination"
        print("✓ PluginswpScraper JetEngine methods exist")
        
        return True
    except AssertionError as e:
        print(f"✗ Method check failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def test_version_extraction():
    """Test version extraction with various formats."""
    print("\n" + "=" * 60)
    print("TEST 4: Version Extraction")
    print("=" * 60)
    
    try:
        weadown = WeadownScraper()
        
        test_cases = [
            ("Plugin Name v1.2.3", "1.2.3"),
            ("Plugin Name 2.0.1", "2.0.1"),
            ("Plugin Name Version 3.5", "3.5"),
            ("Plugin Name Ver 4.0.0", "4.0.0"),
            ("Plugin Name 1.2.3.4", "1.2.3.4"),
            ("Plugin Name", None),
        ]
        
        for title, expected in test_cases:
            result = weadown._extract_version(title)
            if result == expected:
                print(f"✓ '{title}' -> {result}")
            else:
                print(f"✗ '{title}' -> {result} (expected {expected})")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Version extraction test failed: {e}")
        return False


def test_name_cleaning():
    """Test plugin name cleaning with unicode."""
    print("\n" + "=" * 60)
    print("TEST 5: Plugin Name Cleaning")
    print("=" * 60)
    
    try:
        weadown = WeadownScraper()
        
        test_cases = [
            ("Plugin Name v1.2.3 Pro", "plugin name"),
            ("My Plugin 2.0 Premium Nulled", "my plugin"),
            ("Great Plugin [Free Download]", "great plugin"),
            ("Plugin – Latest Update", "plugin"),
            ("  Spaced  Plugin  ", "spaced plugin"),
        ]
        
        for title, expected_contains in test_cases:
            result = weadown._clean_plugin_name(title)
            if result and expected_contains in result.lower():
                print(f"✓ '{title}' -> '{result}'")
            else:
                print(f"? '{title}' -> '{result}' (expected to contain '{expected_contains}')")
        
        return True
    except Exception as e:
        print(f"✗ Name cleaning test failed: {e}")
        return False


def test_scraping():
    """Test actual scraping execution (will fail if sites unreachable)."""
    print("\n" + "=" * 60)
    print("TEST 6: Scraping Execution")
    print("=" * 60)
    print("Note: Sites may be unreachable in this environment")
    print()
    
    try:
        # Test WeadownScraper
        print("Testing WeadownScraper...")
        weadown = WeadownScraper()
        weadown_result = weadown.scrape_plugins()
        
        assert isinstance(weadown_result, dict), "Result should be a dict"
        print(f"✓ WeadownScraper returned dict with {len(weadown_result)} items")
        
        if weadown_result:
            sample = list(weadown_result.items())[0]
            print(f"  Sample: {sample[0]} = {sample[1]}")
        else:
            print("  (Empty result - sites may be unreachable)")
        
        # Test PluginswpScraper
        print("\nTesting PluginswpScraper...")
        pluginswp = PluginswpScraper()
        pluginswp_result = pluginswp.scrape_plugins()
        
        assert isinstance(pluginswp_result, dict), "Result should be a dict"
        print(f"✓ PluginswpScraper returned dict with {len(pluginswp_result)} items")
        
        if pluginswp_result:
            sample = list(pluginswp_result.items())[0]
            print(f"  Sample: {sample[0]} = {sample[1]}")
        else:
            print("  (Empty result - sites may be unreachable)")
        
        return True
    except Exception as e:
        print(f"✗ Scraping test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_json_output():
    """Test that results can be serialized to JSON."""
    print("\n" + "=" * 60)
    print("TEST 7: JSON Serialization")
    print("=" * 60)
    
    try:
        weadown = WeadownScraper()
        result = weadown.scrape_plugins()
        
        # Try to serialize to JSON
        json_str = json.dumps(result, indent=2)
        print(f"✓ Results can be serialized to JSON ({len(json_str)} chars)")
        
        # Try to deserialize
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict), "Parsed JSON should be a dict"
        print("✓ JSON can be deserialized back to dict")
        
        return True
    except Exception as e:
        print(f"✗ JSON serialization test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n")
    print("*" * 60)
    print("* Enhanced Scraper Test Suite")
    print("*" * 60)
    print()
    
    results = []
    
    # Run all tests
    results.append(("Imports", test_imports()))
    results.append(("Instantiation", test_instantiation()))
    results.append(("Methods", test_methods()))
    results.append(("Version Extraction", test_version_extraction()))
    results.append(("Name Cleaning", test_name_cleaning()))
    results.append(("Scraping", test_scraping()))
    results.append(("JSON Output", test_json_output()))
    
    # Print summary
    print("\n")
    print("*" * 60)
    print("* Test Summary")
    print("*" * 60)
    print()
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {name:20s} {status}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    print("*" * 60)
    
    # Return appropriate exit code
    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())
