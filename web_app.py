"""
Flask web application for viewing comparison history and controlling runs.
"""
from flask import Flask, render_template, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging

from src.app import ComparisonRunner
from src.config import Config
from src.database import Database
from src.scraper_coordinator import ScraperCoordinator
from src.scraper import WeadownScraper, PluginswpScraper, ThemeScraperForWeadown, ThemeScraperForPluginsWp
from src.comparator import PluginComparator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

# Initialize components
config = Config()
runner = ComparisonRunner()
db = Database(config.DATABASE_PATH)
coordinator = ScraperCoordinator(worker_pool_size=4)

# Register scraper tasks
coordinator.register_task('pw_plugins', PluginswpScraper)
coordinator.register_task('pw_themes', ThemeScraperForPluginsWp)
coordinator.register_task('wd_plugins', WeadownScraper)
coordinator.register_task('wd_themes', ThemeScraperForWeadown)

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()


def scheduled_comparison():
    """Function to run on schedule."""
    logger.info("Running scheduled comparison...")
    runner.run_comparison()


# Schedule daily run if enabled
if config.SCHEDULE_ENABLED:
    scheduler.add_job(
        scheduled_comparison,
        'cron',
        hour=config.SCHEDULE_HOUR,
        minute=config.SCHEDULE_MINUTE,
        id='daily_comparison'
    )
    logger.info(f"Scheduled daily comparison at {config.SCHEDULE_HOUR:02d}:{config.SCHEDULE_MINUTE:02d}")


@app.route('/')
def index():
    """Main page showing comparison history."""
    return render_template('index.html')


@app.route('/api/scrape/plugins-wp/plugins', methods=['POST'])
def trigger_pw_plugin_scrape():
    """Start scraping plugins from plugins-wp.online."""
    page_limit = request.json.get('max_pages', 5) if request.json else 5
    coordinator.register_task('pw_plugins', PluginswpScraper, page_limit)
    started = coordinator.execute_task('pw_plugins')
    if started:
        return jsonify({'msg': 'Scraping initiated', 'state': 'active'})
    return jsonify({'error': 'Task already running'}), 400


@app.route('/api/scrape/plugins-wp/themes', methods=['POST'])
def trigger_pw_theme_scrape():
    """Start scraping themes from plugins-wp.online."""
    page_limit = request.json.get('max_pages', 5) if request.json else 5
    coordinator.register_task('pw_themes', ThemeScraperForPluginsWp, page_limit)
    started = coordinator.execute_task('pw_themes')
    if started:
        return jsonify({'msg': 'Scraping initiated', 'state': 'active'})
    return jsonify({'error': 'Task already running'}), 400


@app.route('/api/scrape/weadown/plugins', methods=['POST'])
def trigger_wd_plugin_scrape():
    """Start scraping plugins from weadown.com."""
    page_limit = request.json.get('max_pages', 5) if request.json else 5
    coordinator.register_task('wd_plugins', WeadownScraper, page_limit)
    started = coordinator.execute_task('wd_plugins')
    if started:
        return jsonify({'msg': 'Scraping initiated', 'state': 'active'})
    return jsonify({'error': 'Task already running'}), 400


@app.route('/api/scrape/weadown/themes', methods=['POST'])
def trigger_wd_theme_scrape():
    """Start scraping themes from weadown.com."""
    page_limit = request.json.get('max_pages', 5) if request.json else 5
    coordinator.register_task('wd_themes', ThemeScraperForWeadown, page_limit)
    started = coordinator.execute_task('wd_themes')
    if started:
        return jsonify({'msg': 'Scraping initiated', 'state': 'active'})
    return jsonify({'error': 'Task already running'}), 400


@app.route('/api/compare', methods=['POST'])
def perform_comparison():
    """Execute comparison between scraped datasets."""
    # Retrieve all scraped data
    pw_plugin_data = coordinator.retrieve_data('pw_plugins')
    pw_theme_data = coordinator.retrieve_data('pw_themes')
    wd_plugin_data = coordinator.retrieve_data('wd_plugins')
    wd_theme_data = coordinator.retrieve_data('wd_themes')
    
    # Merge collections
    weadown_combined = {**wd_plugin_data, **wd_theme_data}
    pluginswp_combined = {**pw_plugin_data, **pw_theme_data}
    
    if not weadown_combined and not pluginswp_combined:
        return jsonify({'error': 'No scraped data available'}), 400
    
    try:
        comparator = PluginComparator()
        diffs = comparator.compare(weadown_combined, pluginswp_combined)
        comp_id = db.save_comparison(diffs)
        
        return jsonify({
            'msg': 'Comparison finished',
            'id': comp_id,
            'diff_count': len(diffs),
            'diffs': diffs
        })
    except Exception as err:
        logger.error(f"Comparison error: {err}")
        return jsonify({'error': str(err)}), 500


@app.route('/api/comparisons')
def get_comparisons():
    """API endpoint to get all comparisons."""
    comparisons = db.get_all_comparisons()
    return jsonify(comparisons)


@app.route('/api/comparison/<int:comparison_id>')
def get_comparison(comparison_id):
    """API endpoint to get details of a specific comparison."""
    comparison = db.get_comparison_details(comparison_id)
    if comparison:
        return jsonify(comparison)
    return jsonify({'error': 'Comparison not found'}), 404


@app.route('/api/run', methods=['POST'])
def run_comparison():
    """API endpoint to trigger a comparison run."""
    if runner.is_running():
        return jsonify({'error': 'Comparison already running'}), 400
    
    success = runner.run_comparison_async()
    if success:
        return jsonify({'message': 'Comparison started', 'status': 'running'})
    return jsonify({'error': 'Failed to start comparison'}), 500


@app.route('/api/stop', methods=['POST'])
def stop_comparison():
    """API endpoint to stop a running comparison."""
    if runner.stop():
        return jsonify({'message': 'Comparison stopped', 'status': 'stopped'})
    return jsonify({'error': 'No comparison running'}), 400


@app.route('/api/status')
def get_status():
    """API endpoint to get current status with scraper details."""
    all_scraper_info = coordinator.get_all_status()
    return jsonify({
        'running': runner.is_running(),
        'smtp_configured': config.is_configured(),
        'schedule_enabled': config.SCHEDULE_ENABLED,
        'schedule_time': f"{config.SCHEDULE_HOUR:02d}:{config.SCHEDULE_MINUTE:02d}",
        'scrapers': {
            'plugins_wp_plugins': all_scraper_info.get('pw_plugins', {}),
            'plugins_wp_themes': all_scraper_info.get('pw_themes', {}),
            'weadown_plugins': all_scraper_info.get('wd_plugins', {}),
            'weadown_themes': all_scraper_info.get('wd_themes', {})
        }
    })


@app.route('/api/config')
def get_config():
    """API endpoint to get configuration status."""
    validation_errors = config.validate()
    return jsonify({
        'smtp_configured': config.is_configured(),
        'smtp_host': config.SMTP_HOST,
        'smtp_port': config.SMTP_PORT,
        'smtp_from': config.SMTP_FROM,
        'smtp_to': config.SMTP_TO,
        'schedule_enabled': config.SCHEDULE_ENABLED,
        'schedule_time': f"{config.SCHEDULE_HOUR:02d}:{config.SCHEDULE_MINUTE:02d}",
        'validation_errors': validation_errors
    })


def main():
    """Run the Flask application."""
    logger.info(f"Starting web server on port {config.FLASK_PORT}...")
    logger.info(f"Access the UI at http://localhost:{config.FLASK_PORT}")
    app.run(host='0.0.0.0', port=config.FLASK_PORT, debug=False)


if __name__ == '__main__':
    main()
