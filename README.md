# ComparadorPlugins 🔌

Aplicación Python para comparar versiones de plugins y temas de WordPress entre [plugins-wp.online](https://plugins-wp.online) y [weadown.com](https://weadown.com). La herramienta scrapea automáticamente ambos sitios, identifica diferencias de versiones con un umbral de similitud del 80%, y proporciona interfaces CLI y web para visualización.

## Características

- 🔍 **Scraping Automatizado**: Extrae datos de plugins y temas de ambos sitios web
- 📊 **Comparación con Umbral 80%**: Identifica coincidencias exactas y similares con difflib
- 📁 **Exportación a CSV**: Guarda resultados en archivos CSV organizados
- 🖥️ **Interfaz CLI**: Script `run_all.py` para ejecutar todo el flujo desde terminal
- 🌐 **Interfaz Web**: Flask con tabs, filtros, búsqueda y actualización en tiempo real
- 🎨 **Diseño Moderno**: Gradiente púrpura con tarjetas de estadísticas coloridas
- ⚡ **Threading**: Ejecución de scrapers en background sin bloquear la UI

## Requisitos

- Python 3.7 o superior
- pip (instalador de paquetes de Python)

## Instalación

1. **Clonar el repositorio**:
```bash
git clone https://github.com/Navas2025/ComparadorPlugins.git
cd ComparadorPlugins
```

2. **Crear entorno virtual** (recomendado):
```bash
python3 -m venv venv

# En Windows
venv\Scripts\activate

# En Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

## Estructura del Proyecto

```
ComparadorPlugins/
├── scrapers/
│   ├── scraper_plugins_wp.py        # Scrapea plugins de plugins-wp.online
│   ├── scraper_plugins_weadown.py   # Scrapea plugins de weadown.com
│   ├── scraper_temas_wp.py          # Scrapea temas de plugins-wp.online
│   └── scraper_temas_weadown.py     # Scrapea temas de weadown.com
├── comparadores/
│   ├── comparacion_plugins.py       # Compara plugins (umbral 80%)
│   └── comparacion_temas.py         # Compara temas (umbral 80%)
├── data/                            # CSVs generados automáticamente
│   ├── plugins_wp.csv               # Plugins scrapeados de plugins-wp.online
│   ├── plugins_weadown.csv          # Plugins scrapeados de weadown.com
│   ├── temas_wp.csv                 # Temas scrapeados de plugins-wp.online
│   ├── temas_weadown.csv            # Temas scrapeados de weadown.com
│   ├── comparacion_plugins_exactas.csv      # Coincidencias 100%
│   ├── comparacion_plugins_similares.csv    # Coincidencias 80-99%
│   ├── plugins_desactualizados.csv          # Plugins con versión antigua
│   ├── plugins_faltantes.csv                # Plugins no encontrados en WP
│   ├── comparacion_temas_exactas.csv        # Coincidencias 100%
│   ├── comparacion_temas_similares.csv      # Coincidencias 80-99%
│   ├── temas_desactualizados.csv            # Temas con versión antigua
│   └── temas_faltantes.csv                  # Temas no encontrados en WP
├── templates/
│   └── index.html                   # Interfaz web con tabs y filtros
├── web_app.py                       # Aplicación Flask
├── run_all.py                       # Script CLI para ejecutar todo
├── requirements.txt                 # Dependencias del proyecto
└── README.md                        # Este archivo
```

## Uso

### 1. Interfaz de Línea de Comandos (CLI)

Ejecutar todo el flujo de scraping y comparación con un solo comando:

```bash
python3 run_all.py
```

Este script ejecuta en secuencia:
1. Scraping de plugins de plugins-wp.online
2. Scraping de plugins de weadown.com
3. Scraping de temas de plugins-wp.online
4. Scraping de temas de weadown.com
5. Comparación de plugins
6. Comparación de temas

Los resultados se guardan automáticamente en la carpeta `data/`.

### 2. Interfaz Web

Iniciar el servidor web Flask:

```bash
python3 web_app.py
```

La interfaz estará disponible en: **http://localhost:8000**

#### Características de la Interfaz Web:

- ✅ **Tabs**: Alterna entre Plugins y Temas
- ✅ **Estadísticas**: Tarjetas con coincidencias, desactualizados y faltantes
- ✅ **Filtros**: Todos, Exactos, Similares, Desactualizados
- ✅ **Búsqueda**: Campo de búsqueda en tiempo real
- ✅ **Botón "Scrapear Todo"**: Ejecuta el flujo completo en background
- ✅ **Barra de progreso**: Actualización en tiempo real del scraping
- ✅ **Tabla detallada**: Con versiones, estado y enlaces de descarga

### 3. Ejecutar Scrapers Individuales

Puedes ejecutar scrapers individualmente si necesitas actualizar solo una fuente:

```bash
# Scrapear solo plugins de plugins-wp.online
python3 scrapers/scraper_plugins_wp.py

# Scrapear solo plugins de weadown.com
python3 scrapers/scraper_plugins_weadown.py

# Scrapear solo temas de plugins-wp.online
python3 scrapers/scraper_temas_wp.py

# Scrapear solo temas de weadown.com
python3 scrapers/scraper_temas_weadown.py
```

### 4. Ejecutar Comparadores Individuales

```bash
# Comparar solo plugins
python3 comparadores/comparacion_plugins.py

# Comparar solo temas
python3 comparadores/comparacion_temas.py
```

## Cómo Funciona

### 1. Scraping
Los scrapers utilizan `requests` y `BeautifulSoup4` para extraer información de:
- **plugins-wp.online**: Categorías de plugins y temas
- **weadown.com**: Listados de plugins y temas de WordPress

Cada scraper extrae:
- Nombre del plugin/tema (limpio, sin versión)
- Versión
- URL del producto
- Título original

### 2. Comparación con Umbral 80%

Los comparadores utilizan `difflib.SequenceMatcher` para calcular la similitud entre nombres:

```python
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()
```

**Clasificación**:
- **100%**: Coincidencia exacta
- **80-99%**: Coincidencia similar (ej: "elementor pro" vs "elementor")
- **<80%**: No se considera coincidencia

### 3. Comparación de Versiones

Las versiones se comparan como tuplas de números:
- `3.18.1` vs `3.18.3` → `DESACTUALIZADO`
- `8.5.2` vs `8.5.2` → `IGUAL`
- `22.0` vs `21.7` → `ACTUALIZADO`

### 4. Archivos CSV Generados

**Para Plugins**:
- `comparacion_plugins_exactas.csv`: Coincidencias 100%
- `comparacion_plugins_similares.csv`: Coincidencias 80-99%
- `plugins_desactualizados.csv`: Plugins con versión antigua en WP
- `plugins_faltantes.csv`: Plugins en Weadown pero no en WP

**Para Temas**:
- `comparacion_temas_exactas.csv`: Coincidencias 100%
- `comparacion_temas_similares.csv`: Coincidencias 80-99%
- `temas_desactualizados.csv`: Temas con versión antigua en WP
- `temas_faltantes.csv`: Temas en Weadown pero no en WP

## Configuración Avanzada

### Ajustar el Umbral de Similitud

Para cambiar el umbral del 80%, edita los archivos en `comparadores/`:

```python
# En comparacion_plugins.py o comparacion_temas.py
if best_similarity >= 0.80:  # Cambiar a 0.90 para 90%, etc.
    # ...
```

### Ajustar Páginas a Scrapear

Por defecto, cada scraper procesa 5 páginas. Para cambiar esto:

```python
# En cualquier scraper
if __name__ == '__main__':
    plugins = scrape_plugins_wp(max_pages=10)  # Cambiar número
```

### Cambiar Puerto del Servidor Web

Edita `web_app.py`:

```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)  # Cambiar puerto
```

## Solución de Problemas

### Los scrapers no encuentran datos
- Verifica tu conexión a internet
- Los sitios web pueden haber cambiado su estructura HTML
- Revisa los selectores CSS en los scrapers
- Aumenta el timeout en las peticiones HTTP

### El servidor web no inicia
- Asegúrate de que Flask está instalado: `pip install Flask`
- Verifica que el puerto 8000 no esté en uso
- Cambia el puerto en `web_app.py` si es necesario

### Los CSVs están vacíos
- Ejecuta los scrapers individualmente para verificar errores
- Revisa que la carpeta `data/` tiene permisos de escritura
- En Linux/Mac: `chmod 755 data/`

### Problemas de encoding en Windows
- Asegúrate de usar `encoding='utf-8'` al abrir archivos
- Usa un editor de texto con soporte UTF-8

## Desarrollo

### Agregar Nuevos Scrapers

Crea un nuevo archivo en `scrapers/` siguiendo esta estructura:

```python
import requests
from bs4 import BeautifulSoup
import csv

def scrape_mi_sitio():
    # Tu lógica de scraping
    pass

def save_to_csv(data, filename):
    # Guardar en data/
    pass

if __name__ == '__main__':
    data = scrape_mi_sitio()
    save_to_csv(data, 'mi_sitio.csv')
```

### Personalizar la Interfaz Web

Edita `templates/index.html` para cambiar:
- Colores y gradientes
- Texto y etiquetas
- Estructura de las tablas
- Filtros y búsqueda

## Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## Licencia

Este proyecto se proporciona tal cual para uso educativo y personal.

## Soporte

Para problemas, preguntas o sugerencias, abre un issue en GitHub.

---

**Nota**: Esta herramienta está diseñada para uso personal. Por favor respeta los términos de servicio de los sitios web que se scrapean y asegúrate de tener permiso para extraer su contenido.
