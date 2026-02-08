#!/usr/bin/env python3
"""
Flask web application with modular scraping and editable comparisons
Complete web interface with independent scrapers and threshold control
"""
from flask import Flask, render_template, redirect, jsonify, request
import subprocess
import threading
import os
import csv
import sys
import json
from datetime import datetime

app = Flask(__name__)

# Estado global de cada scraper independiente
scraper_status = {
    "pluginswp_plugins": {"running": False, "progress": 0, "message": "IDLE"},
    "pluginswp_themes": {"running": False, "progress": 0, "message": "IDLE"},
    "weadown_plugins": {"running": False, "progress": 0, "message": "IDLE"},
    "weadown_themes": {"running": False, "progress": 0, "message": "IDLE"},
    "compare_plugins": {"running": False, "progress": 0, "message": "IDLE"},
    "compare_themes": {"running": False, "progress": 0, "message": "IDLE"}
}

# Almacenar PIDs de procesos en background
active_processes = {}

# Helper functions
def load_json_config(filename):
    """Load JSON configuration file"""
    filepath = os.path.join('config', filename)
    if not os.path.exists(filepath):
        return {} if 'manual' in filename else {'plugins': [], 'themes': []}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {} if 'manual' in filename else {'plugins': [], 'themes': []}

def save_json_config(filename, data):
    """Save JSON configuration file"""
    os.makedirs('config', exist_ok=True)
    filepath = os.path.join('config', filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def run_scraper_background(script_path, scraper_id, args=None):
    """Execute scraper script in background"""
    global scraper_status, active_processes
    
    scraper_status[scraper_id]["running"] = True
    scraper_status[scraper_id]["progress"] = 10
    scraper_status[scraper_id]["message"] = "Iniciando..."
    
    try:
        # Build command
        cmd = [sys.executable, script_path]
        if args:
            cmd.extend(args)
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        active_processes[scraper_id] = process
        scraper_status[scraper_id]["progress"] = 50
        scraper_status[scraper_id]["message"] = "Scrapeando..."
        
        # Wait for completion
        process.wait()
        
        if process.returncode == 0:
            scraper_status[scraper_id]["progress"] = 100
            scraper_status[scraper_id]["message"] = "Completado ✓"
        else:
            scraper_status[scraper_id]["progress"] = 0
            scraper_status[scraper_id]["message"] = "Error ✗"
            
    except Exception as e:
        scraper_status[scraper_id]["progress"] = 0
        scraper_status[scraper_id]["message"] = f"Error: {str(e)}"
    finally:
        scraper_status[scraper_id]["running"] = False
        if scraper_id in active_processes:
            del active_processes[scraper_id]

def load_csv_data(filename):
    """Carga datos de un archivo CSV"""
    filepath = os.path.join('data', filename)
    if not os.path.exists(filepath):
        return []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception:
        return []

def get_all_plugins_with_comparisons(threshold=80):
    """Load all plugins from plugins-wp with comparison data"""
    # Load base data
    pw_plugins = load_csv_data('plugins_wp.csv')
    
    # Load comparison data
    exact_matches = load_csv_data('comparacion_plugins_exactas.csv')
    similar_matches = load_csv_data('comparacion_plugins_similares.csv')
    
    # Load config
    manual_matches = load_json_config('manual_matches.json').get('plugins', {})
    blacklist = load_json_config('blacklist.json').get('plugins', [])
    blacklist_names = [item['name'] for item in blacklist]
    
    # Merge data
    result = []
    for plugin in pw_plugins:
        plugin_name = plugin.get('nombre', '').strip()
        
        # Check if blacklisted
        if plugin_name in blacklist_names:
            plugin['blacklisted'] = True
            plugin['match_type'] = 'blacklisted'
        else:
            plugin['blacklisted'] = False
            
            # Check manual match first
            if plugin_name in manual_matches:
                manual = manual_matches[plugin_name]
                plugin['match_type'] = 'manual'
                plugin['match_name'] = manual.get('weadown_name', '')
                plugin['match_url'] = manual.get('weadown_url', '')
                plugin['match_version'] = manual.get('weadown_version', '')
                plugin['similarity'] = 100
            else:
                # Check exact match
                exact = next((m for m in exact_matches if m.get('nombre_wp', '').strip() == plugin_name), None)
                if exact:
                    plugin['match_type'] = 'exact'
                    plugin['match_name'] = exact.get('nombre_weadown', '')
                    plugin['match_url'] = exact.get('url_weadown', '')
                    plugin['match_version'] = exact.get('version_weadown', '')
                    plugin['similarity'] = 100
                else:
                    # Check similar match
                    similar = next((m for m in similar_matches if m.get('nombre_wp', '').strip() == plugin_name), None)
                    if similar:
                        plugin['match_type'] = 'similar'
                        plugin['match_name'] = similar.get('nombre_weadown', '')
                        plugin['match_url'] = similar.get('url_weadown', '')
                        plugin['match_version'] = similar.get('version_weadown', '')
                        plugin['similarity'] = float(similar.get('similitud', '0').replace('%', ''))
                    else:
                        plugin['match_type'] = 'none'
                        plugin['similarity'] = 0
        
        result.append(plugin)
    
    return result

def get_all_themes_with_comparisons(threshold=80):
    """Load all themes from plugins-wp with comparison data"""
    # Load base data
    pw_themes = load_csv_data('temas_wp.csv')
    
    # Load comparison data
    exact_matches = load_csv_data('comparacion_temas_exactas.csv')
    similar_matches = load_csv_data('comparacion_temas_similares.csv')
    
    # Load config
    manual_matches = load_json_config('manual_matches.json').get('themes', {})
    blacklist = load_json_config('blacklist.json').get('themes', [])
    blacklist_names = [item['name'] for item in blacklist]
    
    # Merge data
    result = []
    for theme in pw_themes:
        theme_name = theme.get('nombre', '').strip()
        
        # Check if blacklisted
        if theme_name in blacklist_names:
            theme['blacklisted'] = True
            theme['match_type'] = 'blacklisted'
        else:
            theme['blacklisted'] = False
            
            # Check manual match first
            if theme_name in manual_matches:
                manual = manual_matches[theme_name]
                theme['match_type'] = 'manual'
                theme['match_name'] = manual.get('weadown_name', '')
                theme['match_url'] = manual.get('weadown_url', '')
                theme['match_version'] = manual.get('weadown_version', '')
                theme['similarity'] = 100
            else:
                # Check exact match
                exact = next((m for m in exact_matches if m.get('nombre_wp', '').strip() == theme_name), None)
                if exact:
                    theme['match_type'] = 'exact'
                    theme['match_name'] = exact.get('nombre_weadown', '')
                    theme['match_url'] = exact.get('url_weadown', '')
                    theme['match_version'] = exact.get('version_weadown', '')
                    theme['similarity'] = 100
                else:
                    # Check similar match
                    similar = next((m for m in similar_matches if m.get('nombre_wp', '').strip() == theme_name), None)
                    if similar:
                        theme['match_type'] = 'similar'
                        theme['match_name'] = similar.get('nombre_weadown', '')
                        theme['match_url'] = similar.get('url_weadown', '')
                        theme['match_version'] = similar.get('version_weadown', '')
                        theme['similarity'] = float(similar.get('similitud', '0').replace('%', ''))
                    else:
                        theme['match_type'] = 'none'
                        theme['similarity'] = 0
        
        result.append(theme)
    
    return result

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

# ============ Scraping Endpoints ============

@app.route('/api/scrape/pluginswp/plugins', methods=['POST'])
def scrape_pluginswp_plugins():
    """Trigger scraper for plugins-wp.online plugins"""
    if not scraper_status["pluginswp_plugins"]["running"]:
        thread = threading.Thread(
            target=run_scraper_background,
            args=('scrapers/scraper_plugins_wp.py', 'pluginswp_plugins')
        )
        thread.daemon = True
        thread.start()
        return jsonify({"status": "started", "message": "Scraping plugins from plugins-wp.online"})
    return jsonify({"status": "already_running", "message": "Scraper already running"}), 400

@app.route('/api/scrape/pluginswp/themes', methods=['POST'])
def scrape_pluginswp_themes():
    """Trigger scraper for plugins-wp.online themes"""
    if not scraper_status["pluginswp_themes"]["running"]:
        thread = threading.Thread(
            target=run_scraper_background,
            args=('scrapers/scraper_temas_wp.py', 'pluginswp_themes')
        )
        thread.daemon = True
        thread.start()
        return jsonify({"status": "started", "message": "Scraping themes from plugins-wp.online"})
    return jsonify({"status": "already_running", "message": "Scraper already running"}), 400

@app.route('/api/scrape/weadown/plugins', methods=['POST'])
def scrape_weadown_plugins():
    """Trigger scraper for weadown.com plugins"""
    if not scraper_status["weadown_plugins"]["running"]:
        thread = threading.Thread(
            target=run_scraper_background,
            args=('scrapers/scraper_plugins_weadown.py', 'weadown_plugins')
        )
        thread.daemon = True
        thread.start()
        return jsonify({"status": "started", "message": "Scraping plugins from weadown.com"})
    return jsonify({"status": "already_running", "message": "Scraper already running"}), 400

@app.route('/api/scrape/weadown/themes', methods=['POST'])
def scrape_weadown_themes():
    """Trigger scraper for weadown.com themes"""
    if not scraper_status["weadown_themes"]["running"]:
        thread = threading.Thread(
            target=run_scraper_background,
            args=('scrapers/scraper_temas_weadown.py', 'weadown_themes')
        )
        thread.daemon = True
        thread.start()
        return jsonify({"status": "started", "message": "Scraping themes from weadown.com"})
    return jsonify({"status": "already_running", "message": "Scraper already running"}), 400

@app.route('/api/compare/plugins', methods=['POST'])
def compare_plugins():
    """Trigger plugin comparison with threshold"""
    data = request.get_json() or {}
    threshold = data.get('threshold', 80)
    
    if not scraper_status["compare_plugins"]["running"]:
        thread = threading.Thread(
            target=run_scraper_background,
            args=('comparadores/comparacion_plugins.py', 'compare_plugins', ['--threshold', str(threshold)])
        )
        thread.daemon = True
        thread.start()
        return jsonify({"status": "started", "message": f"Comparing plugins with threshold {threshold}%"})
    return jsonify({"status": "already_running", "message": "Comparison already running"}), 400

@app.route('/api/compare/themes', methods=['POST'])
def compare_themes():
    """Trigger theme comparison with threshold"""
    data = request.get_json() or {}
    threshold = data.get('threshold', 80)
    
    if not scraper_status["compare_themes"]["running"]:
        thread = threading.Thread(
            target=run_scraper_background,
            args=('comparadores/comparacion_temas.py', 'compare_themes', ['--threshold', str(threshold)])
        )
        thread.daemon = True
        thread.start()
        return jsonify({"status": "started", "message": f"Comparing themes with threshold {threshold}%"})
    return jsonify({"status": "already_running", "message": "Comparison already running"}), 400

# ============ Data Endpoints ============

@app.route('/api/data/plugins', methods=['GET'])
def get_plugins_data():
    """Get all plugins with comparison data"""
    threshold = request.args.get('threshold', 80, type=int)
    plugins = get_all_plugins_with_comparisons(threshold)
    return jsonify({"data": plugins, "count": len(plugins)})

@app.route('/api/data/themes', methods=['GET'])
def get_themes_data():
    """Get all themes with comparison data"""
    threshold = request.args.get('threshold', 80, type=int)
    themes = get_all_themes_with_comparisons(threshold)
    return jsonify({"data": themes, "count": len(themes)})

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get scraping status for all scrapers"""
    return jsonify(scraper_status)

# ============ Configuration Endpoints ============

@app.route('/api/config/manual-match', methods=['POST'])
def save_manual_match():
    """Save manual URL match"""
    data = request.get_json()
    
    if not data or 'type' not in data or 'name' not in data or 'weadown_url' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    match_type = data['type']  # 'plugins' or 'themes'
    name = data['name']
    
    config = load_json_config('manual_matches.json')
    if match_type not in config:
        config[match_type] = {}
    
    config[match_type][name] = {
        "weadown_url": data['weadown_url'],
        "weadown_name": data.get('weadown_name', ''),
        "weadown_version": data.get('weadown_version', ''),
        "date_added": datetime.now().isoformat()
    }
    
    if save_json_config('manual_matches.json', config):
        return jsonify({"status": "success", "message": "Manual match saved"})
    return jsonify({"error": "Failed to save"}), 500

@app.route('/api/config/blacklist', methods=['GET'])
def get_blacklist():
    """Get blacklist items"""
    config = load_json_config('blacklist.json')
    return jsonify(config)

@app.route('/api/config/blacklist', methods=['POST'])
def add_to_blacklist():
    """Add plugin/theme to blacklist"""
    data = request.get_json()
    
    if not data or 'type' not in data or 'name' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    match_type = data['type']  # 'plugins' or 'themes'
    name = data['name']
    reason = data.get('reason', 'User blacklisted')
    
    config = load_json_config('blacklist.json')
    if match_type not in config:
        config[match_type] = []
    
    # Check if already blacklisted
    if any(item['name'] == name for item in config[match_type]):
        return jsonify({"status": "already_exists", "message": "Already in blacklist"})
    
    config[match_type].append({
        "name": name,
        "date_added": datetime.now().isoformat(),
        "reason": reason
    })
    
    if save_json_config('blacklist.json', config):
        return jsonify({"status": "success", "message": "Added to blacklist"})
    return jsonify({"error": "Failed to save"}), 500

@app.route('/api/config/blacklist/<match_type>/<item_name>', methods=['DELETE'])
def remove_from_blacklist(match_type, item_name):
    """Remove from blacklist"""
    config = load_json_config('blacklist.json')
    
    if match_type not in config:
        return jsonify({"error": "Invalid type"}), 400
    
    config[match_type] = [item for item in config[match_type] if item['name'] != item_name]
    
    if save_json_config('blacklist.json', config):
        return jsonify({"status": "success", "message": "Removed from blacklist"})
    return jsonify({"error": "Failed to save"}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Iniciando servidor web en http://0.0.0.0:8000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=8000, debug=False)
