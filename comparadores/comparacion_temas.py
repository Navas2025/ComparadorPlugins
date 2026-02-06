#!/usr/bin/env python3
"""
Comparador de temas con umbral de similitud del 80%
Compara temas_wp.csv y temas_weadown.csv
Genera archivos de salida con comparaciones
"""
import csv
import os
from difflib import SequenceMatcher

def similarity(a, b):
    """Calcula la similitud entre dos strings (0.0 a 1.0)"""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def compare_versions(v1, v2):
    """
    Compara dos versiones y determina si necesita actualización
    Retorna: "ACTUALIZADO", "DESACTUALIZADO", "IGUAL"
    """
    if not v1 or not v2:
        return "DESCONOCIDO"
    
    try:
        # Convertir versiones a tuplas de números
        parts1 = [int(x) for x in v1.split('.')]
        parts2 = [int(x) for x in v2.split('.')]
        
        # Normalizar longitudes
        max_len = max(len(parts1), len(parts2))
        parts1.extend([0] * (max_len - len(parts1)))
        parts2.extend([0] * (max_len - len(parts2)))
        
        if parts1 > parts2:
            return "ACTUALIZADO"
        elif parts1 < parts2:
            return "DESACTUALIZADO"
        else:
            return "IGUAL"
    except:
        # Si no se puede comparar, hacer comparación simple
        if v1 == v2:
            return "IGUAL"
        return "DESCONOCIDO"

def load_csv(filename):
    """Carga un archivo CSV y retorna una lista de diccionarios"""
    filepath = os.path.join('data', filename)
    if not os.path.exists(filepath):
        print(f"⚠️  Archivo no encontrado: {filepath}")
        return []
    
    temas = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        temas = list(reader)
    
    return temas

def save_csv(data, filename, fieldnames):
    """Guarda datos en un archivo CSV"""
    os.makedirs('data', exist_ok=True)
    filepath = os.path.join('data', filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"  ✓ Guardado: {filepath} ({len(data)} registros)")

def compare_temas():
    """Compara temas de ambas fuentes con umbral del 80%"""
    print("=" * 60)
    print("Comparando temas (umbral 80%)")
    print("=" * 60)
    
    # Cargar datos
    print("\n📂 Cargando archivos...")
    temas_wp = load_csv('temas_wp.csv')
    temas_weadown = load_csv('temas_weadown.csv')
    
    print(f"  ✓ Temas WP: {len(temas_wp)}")
    print(f"  ✓ Temas Weadown: {len(temas_weadown)}")
    
    if not temas_wp or not temas_weadown:
        print("\n❌ No hay datos suficientes para comparar")
        return
    
    # Listas para clasificar coincidencias
    exactas = []           # 100% coincidencia
    similares = []         # 80-99% coincidencia
    desactualizados = []   # Versión más antigua en WP
    faltantes = []         # En Weadown pero no en WP
    
    print("\n🔍 Comparando...")
    
    # Buscar coincidencias para cada tema de Weadown
    matched_wp_indices = set()
    
    for wd_tema in temas_weadown:
        wd_nombre = wd_tema['nombre']
        best_match = None
        best_similarity = 0.0
        best_index = -1
        
        # Buscar mejor coincidencia en WP
        for idx, wp_tema in enumerate(temas_wp):
            if idx in matched_wp_indices:
                continue
            
            wp_nombre = wp_tema['nombre']
            sim = similarity(wd_nombre, wp_nombre)
            
            if sim > best_similarity:
                best_similarity = sim
                best_match = wp_tema
                best_index = idx
        
        # Clasificar según similitud
        if best_similarity >= 0.80:
            matched_wp_indices.add(best_index)
            
            record = {
                'nombre_wp': best_match['nombre'],
                'nombre_weadown': wd_nombre,
                'version_wp': best_match['version'],
                'version_weadown': wd_tema['version'],
                'url_wp': best_match['url'],
                'url_weadown': wd_tema['url'],
                'similitud': f"{best_similarity:.2%}",
                'estado': compare_versions(best_match['version'], wd_tema['version'])
            }
            
            if best_similarity == 1.0:
                exactas.append(record)
            else:
                similares.append(record)
            
            # Si está desactualizado, agregar a la lista
            if record['estado'] == "DESACTUALIZADO":
                desactualizados.append(record)
        else:
            # No hay coincidencia suficiente
            faltantes.append({
                'nombre_weadown': wd_nombre,
                'version_weadown': wd_tema['version'],
                'url_weadown': wd_tema['url'],
                'observacion': 'No encontrado en WP'
            })
    
    # Guardar resultados
    print("\n💾 Guardando resultados...")
    
    fieldnames_comparacion = ['nombre_wp', 'nombre_weadown', 'version_wp', 'version_weadown', 
                              'url_wp', 'url_weadown', 'similitud', 'estado']
    
    save_csv(exactas, 'comparacion_temas_exactas.csv', fieldnames_comparacion)
    save_csv(similares, 'comparacion_temas_similares.csv', fieldnames_comparacion)
    save_csv(desactualizados, 'temas_desactualizados.csv', fieldnames_comparacion)
    
    fieldnames_faltantes = ['nombre_weadown', 'version_weadown', 'url_weadown', 'observacion']
    save_csv(faltantes, 'temas_faltantes.csv', fieldnames_faltantes)
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    print(f"✓ Coincidencias exactas (100%):     {len(exactas)}")
    print(f"✓ Coincidencias similares (80-99%): {len(similares)}")
    print(f"⚠ Temas desactualizados:            {len(desactualizados)}")
    print(f"⚠ Temas faltantes en WP:            {len(faltantes)}")
    print(f"  Total coincidencias:               {len(exactas) + len(similares)}")
    print("=" * 60)

if __name__ == '__main__':
    try:
        compare_temas()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
