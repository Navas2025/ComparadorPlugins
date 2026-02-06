#!/usr/bin/env python3
"""
Flask web application funcional con threading y subprocess
Interfaz web mejorada con scraping en tiempo real
"""
from flask import Flask, render_template, redirect, jsonify
import subprocess
import threading
import os
import csv
import sys

app = Flask(__name__)

# Estado global del scraper
scraper_status = {
    "running": False,
    "progress": "",
    "current_step": 0,
    "total_steps": 6,
    "log": []
}

def run_all_scrapers():
    """Ejecuta todo el flujo de scraping y comparación"""
    global scraper_status
    scraper_status["running"] = True
    scraper_status["log"] = []
    scraper_status["current_step"] = 0
    
    steps = [
        ('scrapers/scraper_plugins_wp.py', 'Plugins plugins-wp.online'),
        ('scrapers/scraper_plugins_weadown.py', 'Plugins weadown.com'),
        ('scrapers/scraper_temas_wp.py', 'Temas plugins-wp.online'),
        ('scrapers/scraper_temas_weadown.py', 'Temas weadown.com'),
        ('comparadores/comparacion_plugins.py', 'Comparación plugins'),
        ('comparadores/comparacion_temas.py', 'Comparación temas')
    ]
    
    for i, (script, description) in enumerate(steps, 1):
        scraper_status["current_step"] = i
        scraper_status["progress"] = f"⏳ {description}..."
        scraper_status["log"].append(f"[{i}/6] {description}")
        
        try:
            result = subprocess.run(
                [sys.executable, script],
                capture_output=True,
                text=True,
                timeout=600,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            if result.returncode == 0:
                scraper_status["log"].append(f"✅ {description} completado")
            else:
                scraper_status["log"].append(f"❌ {description} falló")
                
        except Exception as e:
            scraper_status["log"].append(f"❌ Error en {description}: {str(e)}")
    
    scraper_status["progress"] = "✅ ¡Proceso completado!"
    scraper_status["running"] = False

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

@app.route('/')
def index():
    """Página principal con estadísticas y tablas"""
    # Cargar datos de comparación
    plugins_exactas = load_csv_data('comparacion_plugins_exactas.csv')
    plugins_similares = load_csv_data('comparacion_plugins_similares.csv')
    plugins_desactualizados = load_csv_data('plugins_desactualizados.csv')
    plugins_faltantes = load_csv_data('plugins_faltantes.csv')
    
    temas_exactas = load_csv_data('comparacion_temas_exactas.csv')
    temas_similares = load_csv_data('comparacion_temas_similares.csv')
    temas_desactualizados = load_csv_data('temas_desactualizados.csv')
    temas_faltantes = load_csv_data('temas_faltantes.csv')
    
    # Preparar datos para la vista
    data = {
        'plugins': {
            'exactas': plugins_exactas,
            'similares': plugins_similares,
            'desactualizados': plugins_desactualizados,
            'faltantes': plugins_faltantes,
            'total_coincidencias': len(plugins_exactas) + len(plugins_similares),
            'total_desactualizados': len(plugins_desactualizados),
            'total_faltantes': len(plugins_faltantes)
        },
        'temas': {
            'exactas': temas_exactas,
            'similares': temas_similares,
            'desactualizados': temas_desactualizados,
            'faltantes': temas_faltantes,
            'total_coincidencias': len(temas_exactas) + len(temas_similares),
            'total_desactualizados': len(temas_desactualizados),
            'total_faltantes': len(temas_faltantes)
        }
    }
    
    return render_template('index.html', data=data)

@app.route('/scrapear')
def scrapear():
    """Inicia el proceso de scraping en background"""
    if not scraper_status["running"]:
        thread = threading.Thread(target=run_all_scrapers)
        thread.daemon = True
        thread.start()
    return redirect('/')

@app.route('/status')
def status():
    """Retorna el estado actual del scraping"""
    return jsonify(scraper_status)

@app.route('/editar', methods=['POST'])
def editar():
    """Permite editar coincidencias manualmente (placeholder)"""
    # TODO: Implementar edición manual si es necesario
    return jsonify({'message': 'Función de edición no implementada aún'})

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Iniciando servidor web en http://0.0.0.0:8000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=8000, debug=False)
