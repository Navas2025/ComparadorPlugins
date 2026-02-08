#!/usr/bin/env python3
"""
Scraper para temas de plugins-wp.online
Extrae: nombre, versión, URL
Guarda en: data/temas_wp.csv
"""
import requests
from bs4 import BeautifulSoup
import csv
import re
import os
import time

def extract_version(text):
    """Extrae el número de versión del texto"""
    if not text:
        return ""
    
    patterns = [
        r'v?(\d+\.\d+(?:\.\d+)?(?:\.\d+)?)',
        r'version\s+(\d+\.\d+(?:\.\d+)?)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return ""

def clean_theme_name(title):
    """Extrae el nombre limpio del tema"""
    if not title:
        return ""
    
    # Remover números de versión
    name = re.sub(r'v?\d+\.\d+(?:\.\d+)?(?:\.\d+)?', '', title)
    
    # Remover sufijos comunes
    name = re.sub(r'\b(pro|premium|nulled|free|download|wordpress|theme|version)\b', '', name, flags=re.IGNORECASE)
    
    # Remover todo después de " - " o "|"
    name = re.sub(r'\s+[\-–|]\s+.*$', '', name)
    
    # Limpiar puntuación y espacios
    name = name.strip(' -–|:')
    name = ' '.join(name.lower().split())
    
    return name

def scrape_temas_wp(max_pages=5):
    """
    Scrapea temas de https://plugins-wp.online/categoria-producto/temas/
    """
    print("=" * 60)
    print("Scrapeando temas de plugins-wp.online")
    print("=" * 60)
    
    base_url = "https://plugins-wp.online"
    temas = []
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    for page_num in range(1, max_pages + 1):
        try:
            if page_num == 1:
                url = f"{base_url}/categoria-producto/temas/"
            else:
                url = f"{base_url}/categoria-producto/temas/page/{page_num}/"
            
            print(f"\n📄 Página {page_num}: {url}")
            
            response = session.get(url, timeout=30)
            
            if response.status_code == 404:
                print(f"  ⚠️  No hay más páginas")
                break
            
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar productos (típicamente en WooCommerce)
            products = soup.find_all('li', class_=re.compile(r'product'))
            
            if not products:
                products = soup.find_all('div', class_=re.compile(r'product'))
            
            if not products:
                print(f"  ⚠️  No se encontraron productos")
                break
            
            print(f"  ✓ Encontrados {len(products)} productos")
            
            for product in products:
                try:
                    # Buscar título
                    title_elem = product.find('h2', class_='woocommerce-loop-product__title')
                    if not title_elem:
                        title_elem = product.find(['h2', 'h3'], class_=re.compile(r'product'))
                    if not title_elem:
                        title_elem = product.find(['h2', 'h3'])
                    
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # Buscar enlace
                    link_elem = product.find('a', href=True)
                    url = ""
                    if link_elem:
                        url = link_elem['href']
                        if not url.startswith('http'):
                            url = base_url + url
                    
                    # Extraer versión y nombre
                    version = extract_version(title)
                    theme_name = clean_theme_name(title)
                    
                    if theme_name:
                        temas.append({
                            'nombre': theme_name,
                            'version': version,
                            'url': url,
                            'titulo_original': title
                        })
                
                except Exception as e:
                    print(f"    ⚠️  Error procesando producto: {e}")
                    continue
            
            # Pausa entre páginas
            if page_num < max_pages:
                time.sleep(1)
        
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Error en página {page_num}: {e}")
            break
        except Exception as e:
            print(f"  ❌ Error inesperado en página {page_num}: {e}")
            break
    
    return temas

def save_to_csv(temas, filename):
    """Guarda los temas en un archivo CSV"""
    os.makedirs('data', exist_ok=True)
    filepath = os.path.join('data', filename)
    
    print(f"\n💾 Guardando {len(temas)} temas en {filepath}")
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        if temas:
            writer = csv.DictWriter(f, fieldnames=['nombre', 'version', 'url', 'titulo_original'])
            writer.writeheader()
            writer.writerows(temas)
    
    print(f"✅ Guardado exitosamente")

if __name__ == '__main__':
    try:
        temas = scrape_temas_wp(max_pages=5)
        save_to_csv(temas, 'temas_wp.csv')
        print(f"\n{'=' * 60}")
        print(f"✅ Total: {len(temas)} temas extraídos")
        print(f"{'=' * 60}\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
