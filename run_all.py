#!/usr/bin/env python3
"""
Script para ejecutar todo el flujo de scraping y comparación
Ejecuta los 4 scrapers y los 2 comparadores en secuencia
"""
import subprocess
import sys
import os

def run_script(script_path, description):
    """Ejecuta un script de Python y maneja errores"""
    print(f"\n{'='*60}")
    print(f"Ejecutando: {description}")
    print(f"Script: {script_path}")
    print('='*60)
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            check=True
        )
        
        print(f"\n✅ {description} completado exitosamente")
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error en {description}")
        print(f"Código de salida: {e.returncode}")
        return False
    
    except Exception as e:
        print(f"\n❌ Error inesperado en {description}: {e}")
        return False

def main():
    """Ejecuta todo el flujo de scraping y comparación"""
    print("\n" + "="*60)
    print("🚀 INICIANDO PROCESO COMPLETO DE SCRAPING Y COMPARACIÓN")
    print("="*60)
    
    scripts = [
        ('scrapers/scraper_plugins_wp.py', 'Scraping de Plugins de plugins-wp.online'),
        ('scrapers/scraper_plugins_weadown.py', 'Scraping de Plugins de weadown.com'),
        ('scrapers/scraper_temas_wp.py', 'Scraping de Temas de plugins-wp.online'),
        ('scrapers/scraper_temas_weadown.py', 'Scraping de Temas de weadown.com'),
        ('comparadores/comparacion_plugins.py', 'Comparación de Plugins'),
        ('comparadores/comparacion_temas.py', 'Comparación de Temas')
    ]
    
    results = []
    
    for script_path, description in scripts:
        success = run_script(script_path, description)
        results.append((description, success))
        
        if not success:
            print(f"\n⚠️  Advertencia: {description} falló, pero continuando...")
    
    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN FINAL")
    print("="*60)
    
    for description, success in results:
        status = "✅ ÉXITO" if success else "❌ FALLÓ"
        print(f"{status}: {description}")
    
    failed_count = sum(1 for _, success in results if not success)
    
    if failed_count == 0:
        print("\n✅ ¡Proceso completado exitosamente!")
        print("="*60 + "\n")
        return 0
    else:
        print(f"\n⚠️  Proceso completado con {failed_count} error(es)")
        print("="*60 + "\n")
        return 1

if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
