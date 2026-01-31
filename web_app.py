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
    """API endpoint to get current status."""
    return jsonify({
        'running': runner.is_running(),
        'smtp_configured': config.is_configured(),
        'schedule_enabled': config.SCHEDULE_ENABLED,
        'schedule_time': f"{config.SCHEDULE_HOUR:02d}:{config.SCHEDULE_MINUTE:02d}"
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
