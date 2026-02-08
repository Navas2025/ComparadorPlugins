# Web Interface Features - Implementation Guide

## New Features Implemented

### 1. Configuration System
- **Location**: `config/` directory
- **Files**:
  - `manual_matches.json` - Store manual URL matches
  - `blacklist.json` - Store blacklisted items
- **Format**: JSON with separate sections for plugins and themes
- **Persistence**: All changes persist across server restarts

### 2. REST API Endpoints

#### Scraping Endpoints (Independent)
- `POST /api/scrape/pluginswp/plugins` - Scrape plugins from plugins-wp.online
- `POST /api/scrape/pluginswp/themes` - Scrape themes from plugins-wp.online
- `POST /api/scrape/weadown/plugins` - Scrape plugins from weadown.com
- `POST /api/scrape/weadown/themes` - Scrape themes from weadown.com

#### Comparison Endpoints
- `POST /api/compare/plugins` - Compare plugins with custom threshold
  - Body: `{"threshold": 85}` (80-100)
- `POST /api/compare/themes` - Compare themes with custom threshold
  - Body: `{"threshold": 85}` (80-100)

#### Data Endpoints
- `GET /api/data/plugins?threshold=80` - Get all plugins with comparison data
- `GET /api/data/themes?threshold=80` - Get all themes with comparison data
- `GET /api/status` - Get real-time status of all scrapers

#### Configuration Endpoints
- `POST /api/config/manual-match` - Save manual match
  - Body: `{"type": "plugins", "name": "...", "weadown_url": "...", "weadown_name": "...", "weadown_version": "..."}`
- `GET /api/config/blacklist` - Get blacklist
- `POST /api/config/blacklist` - Add to blacklist
  - Body: `{"type": "plugins", "name": "...", "reason": "..."}`
- `DELETE /api/config/blacklist/<type>/<name>` - Remove from blacklist

### 3. Enhanced Comparison Scripts

#### Command Line Arguments
Both `comparacion_plugins.py` and `comparacion_temas.py` now support:
```bash
python3 comparadores/comparacion_plugins.py --threshold 85
python3 comparadores/comparacion_temas.py --threshold 90
```

#### Blacklist Support
- Scripts automatically load and skip blacklisted items
- No manual intervention needed

### 4. Modern Web Interface

#### Features
- **Two Tabs**: Separate views for Plugins and Temas
- **Independent Scraping**: Individual buttons for each scraper
- **Real-time Progress**: Progress bars for each scraper
- **Threshold Control**: Slider to adjust similarity threshold (80-100%)
- **Stats Dashboard**: 4 cards showing matches, outdated, no-match, and blacklisted counts
- **Search**: Real-time search across all items
- **Filters**: 5 filter buttons (Todos, Con Match, Similares, Sin Match, Desactualizados)
- **Action Buttons**:
  - ⬇️ Download (for outdated items with matches)
  - ✏️ Edit (to manually set weadown URL)
  - 🗑️ Delete (add to blacklist)
- **Edit Modal**: Full form to edit manual matches
- **Responsive Design**: Works on mobile, tablet, and desktop

#### Color Coding
- 🟢 Green badges: Exact matches and up-to-date versions
- 🟡 Yellow badges: Similar matches and outdated versions
- 🔴 Red badges: No matches found
- ⚫ Gray badges: Blacklisted items (with restore option)

### 5. Data Flow

```
1. User clicks "Scrapear PW Plugins" → Backend triggers scraper_plugins_wp.py
2. User clicks "Scrapear WD Plugins" → Backend triggers scraper_plugins_weadown.py
3. User adjusts threshold slider → Frontend updates immediately
4. User clicks "Comparar Plugins" → Backend runs comparison with custom threshold
5. Frontend polls /api/status every 2 seconds → Updates progress bars
6. When comparison completes → Frontend reloads data automatically
7. User sees ALL plugins from plugins-wp.online with match status
```

## Usage Examples

### Starting the Server
```bash
cd /home/runner/work/ComparadorPlugins/ComparadorPlugins
python3 web_app.py
# Access at http://localhost:8000
```

### Manual Match Example
1. Click ✏️ Edit button on any item
2. Fill in the modal:
   - URL de Weadown: `https://weadown.com/plugin-name`
   - Nombre en Weadown: `Exact Plugin Name`
   - Versión en Weadown: `1.2.3`
3. Click "Guardar"
4. Match is saved in `config/manual_matches.json`

### Blacklist Example
1. Click 🗑️ Delete button on any item
2. Confirm the action
3. Item is added to `config/blacklist.json`
4. Item appears grayed out with 🔓 Restore button

### Threshold Adjustment
1. Move the slider from 80% to 95%
2. Table updates immediately (no re-scraping needed)
3. Click "Comparar Plugins" to re-run comparison with new threshold

## Technical Details

### Background Processing
- All scrapers run in separate threads
- Non-blocking - UI remains responsive
- Process tracking via global `scraper_status` dict

### Data Merging Logic
For each plugin/theme from plugins-wp.online:
1. Check if blacklisted → skip
2. Check manual_matches.json → use manual match
3. Check COMPARACION_EXACTA.csv → use exact match
4. Check COMPARACION_SIMILAR.csv → use similar match (if >= threshold)
5. Otherwise → mark as "no match"

### File Structure
```
ComparadorPlugins/
├── config/
│   ├── manual_matches.json    # Manual URL matches
│   └── blacklist.json          # Blacklisted items
├── static/
│   ├── style.css               # Modern responsive CSS
│   └── app.js                  # Frontend JavaScript logic
├── templates/
│   └── index.html              # Main interface template
├── comparadores/
│   ├── comparacion_plugins.py  # Enhanced with --threshold
│   └── comparacion_temas.py    # Enhanced with --threshold
└── web_app.py                  # Flask app with REST API
```

## Browser Compatibility
- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Mobile browsers (responsive design)

## Performance
- Scrapers run independently (can run 4 scrapers simultaneously)
- Frontend polls status every 2 seconds
- Table renders 1000+ items smoothly
- No page reloads needed (SPA-like experience)
