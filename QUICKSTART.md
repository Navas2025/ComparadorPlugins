# Quick Start Guide: Updated ComparadorPlugins

## What's New

The ComparadorPlugins system has been completely updated with:
- ✨ Modern, intuitive web interface
- 🔧 Separate controls for plugins and themes
- 🌐 Support for both Plugins-WP.online and Weadown.com
- ⚡ Real-time status updates
- 📊 Live statistics dashboard

## Getting Started

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/Navas2025/ComparadorPlugins.git
cd ComparadorPlugins

# Install dependencies
pip install -r requirements.txt

# Configure environment (optional)
cp .env.example .env
# Edit .env with your SMTP settings if you want email notifications
```

### 2. Start the Web Interface

```bash
python web_app.py
```

Access the interface at: **http://localhost:5000**

### 3. Using the Interface

#### Scrape Individual Sources

1. **Plugins-WP.online Card**
   - Click "📦 Plugins" to scrape plugins
   - Click "🎨 Temas" to scrape themes
   - Watch the status badge change (PENDING → ACTIVE → FINISHED)
   - See the counter update with items found

2. **Weadown.com Card**
   - Click "📦 Plugins" to scrape plugins
   - Click "🎨 Temas" to scrape themes
   - Monitor progress with real-time status updates

#### Compare Results

1. After scraping from both sources, click **"Comparar Ahora"**
2. The system will:
   - Combine all scraped data
   - Find version differences
   - Display results in the table below

#### Filter and Search

- **Todos**: Show all items
- **Desactualizados**: Show only outdated items
- **Search box**: Filter by plugin/theme name

## Understanding the Interface

### Status Badges

- 🟡 **PENDING**: Task is registered but not started
- 🔵 **ACTIVE**: Currently scraping (animated pulse)
- 🟢 **FINISHED**: Successfully completed
- 🔴 **FAILED**: Error occurred

### Statistics Dashboard

Five boxes show:
1. **PW Plugins**: Plugins found on Plugins-WP.online
2. **PW Temas**: Themes found on Plugins-WP.online
3. **WD Plugins**: Plugins found on Weadown.com
4. **WD Temas**: Themes found on Weadown.com
5. **⚠️ Desactualizados**: Items with version differences

### Comparison Table

Shows:
- **Nombre**: Plugin/theme name
- **Versión Weadown**: Version from Weadown.com
- **Versión Plugins-WP**: Version from Plugins-WP.online
- **Descarga**: Download link (if available)

## API Usage

If you prefer to use the API directly:

### Trigger Scraping

```bash
# Scrape Plugins-WP plugins
curl -X POST http://localhost:5000/api/scrape/plugins-wp/plugins \
  -H "Content-Type: application/json" \
  -d '{"max_pages": 5}'

# Scrape Plugins-WP themes
curl -X POST http://localhost:5000/api/scrape/plugins-wp/themes \
  -H "Content-Type: application/json" \
  -d '{"max_pages": 5}'

# Scrape Weadown plugins
curl -X POST http://localhost:5000/api/scrape/weadown/plugins \
  -H "Content-Type: application/json" \
  -d '{"max_pages": 5}'

# Scrape Weadown themes
curl -X POST http://localhost:5000/api/scrape/weadown/themes \
  -H "Content-Type: application/json" \
  -d '{"max_pages": 5}'
```

### Check Status

```bash
curl http://localhost:5000/api/status | python -m json.tool
```

### Execute Comparison

```bash
curl -X POST http://localhost:5000/api/compare | python -m json.tool
```

## Advanced Configuration

### Adjust Pages to Scrape

Change the `max_pages` parameter in API calls:

```bash
# Scrape 10 pages instead of 5
curl -X POST http://localhost:5000/api/scrape/weadown/plugins \
  -H "Content-Type: application/json" \
  -d '{"max_pages": 10}'
```

### Schedule Automatic Runs

In `.env` file:
```env
SCHEDULE_ENABLED=true
SCHEDULE_HOUR=9
SCHEDULE_MINUTE=0
```

This will run comparisons automatically at 9:00 AM daily.

### Email Notifications

Configure SMTP in `.env`:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com
SMTP_TO=recipient@example.com
```

## Troubleshooting

### Scrapers Return 0 Items

**Possible causes:**
1. Website structure changed
2. Network connectivity issues
3. Rate limiting by website

**Solutions:**
- Check logs for specific errors
- Verify internet connection
- Try again after a few minutes

### Status Shows "FAILED"

Check the application logs:
```bash
# If running in foreground, check console output
# If running in background, check log file
```

Common issues:
- DNS resolution failure
- Connection timeout
- Invalid HTML structure

### UI Not Updating

- Ensure JavaScript is enabled in browser
- Check browser console for errors
- Verify `/api/status` endpoint is responding

## Testing

Run the test suite:

```bash
cd /path/to/ComparadorPlugins
python tests/test_scrapers.py
```

Expected output:
```
============================================================
Running Scraper Tests
============================================================
Testing URL Configuration...
✓ URL configuration tests passed!

Testing ScraperCoordinator...
✓ Coordinator tests passed!

Testing Version Extraction...
✓ Version extraction tests passed!

Testing Name Cleaning...
✓ Name cleaning tests passed!

============================================================
✓ All tests passed successfully!
============================================================
```

## Tips for Best Results

1. **Run scrapers sequentially**: Let one finish before starting another
2. **Use reasonable page limits**: 5-10 pages is usually sufficient
3. **Wait between runs**: Don't hammer the websites
4. **Check status regularly**: Watch for failures
5. **Filter results**: Use "Desactualizados" to focus on differences

## Support

For issues or questions:
1. Check `IMPLEMENTATION_SUMMARY.md` for technical details
2. Review logs for error messages
3. Open an issue on GitHub

## What Changed from Previous Version

- **URLs**: Updated to use correct domains and paths
- **Selectors**: Added support for new HTML structures
- **UI**: Completely redesigned with modern look
- **API**: New granular endpoints for each scraper
- **Architecture**: New coordinator pattern for better task management
- **Testing**: Comprehensive test suite added

---

**Enjoy the improved ComparadorPlugins! 🚀**
