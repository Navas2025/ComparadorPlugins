"""
Command-line interface for the Plugin Comparator.
"""
import argparse
import sys
import logging
from src.app import ComparisonRunner
from src.config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Plugin Comparator - Compare plugin versions between weadown.com and pluginswp.online'
    )
    
    parser.add_argument(
        'action',
        choices=['run', 'status', 'config'],
        help='Action to perform: run (execute comparison), status (check if running), config (show configuration)'
    )
    
    args = parser.parse_args()
    
    if args.action == 'run':
        run_comparison()
    elif args.action == 'status':
        check_status()
    elif args.action == 'config':
        show_config()


def run_comparison():
    """Run the comparison process."""
    logger.info("Starting comparison process...")
    
    runner = ComparisonRunner()
    result = runner.run_comparison()
    
    if result['success']:
        logger.info(f"✓ Comparison completed successfully!")
        logger.info(f"  Found {result['differences_count']} differences")
        logger.info(f"  Comparison ID: {result['comparison_id']}")
        sys.exit(0)
    else:
        logger.error(f"✗ Comparison failed: {result['error']}")
        sys.exit(1)


def check_status():
    """Check if a comparison is running."""
    runner = ComparisonRunner()
    
    if runner.is_running():
        logger.info("Status: RUNNING")
        sys.exit(0)
    else:
        logger.info("Status: IDLE")
        sys.exit(0)


def show_config():
    """Show current configuration."""
    config = Config()
    
    print("\n" + "=" * 60)
    print("Plugin Comparator Configuration")
    print("=" * 60)
    print()
    print("SMTP Configuration:")
    print(f"  Host: {config.SMTP_HOST}")
    print(f"  Port: {config.SMTP_PORT}")
    print(f"  Username: {config.SMTP_USERNAME}")
    print(f"  From: {config.SMTP_FROM}")
    print(f"  To: {config.SMTP_TO}")
    print(f"  Password: {'*' * 8 if config.SMTP_PASSWORD else '(not set)'}")
    print()
    print("Application Configuration:")
    print(f"  Database: {config.DATABASE_PATH}")
    print(f"  Flask Port: {config.FLASK_PORT}")
    print(f"  Schedule Enabled: {config.SCHEDULE_ENABLED}")
    print(f"  Schedule Time: {config.SCHEDULE_HOUR:02d}:{config.SCHEDULE_MINUTE:02d}")
    print()
    
    # Validate configuration
    errors = config.validate()
    if errors:
        print("⚠ Configuration Errors:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease update your .env file to fix these issues.")
    else:
        print("✓ Configuration is valid")
    
    print("=" * 60)
    print()


if __name__ == '__main__':
    main()
