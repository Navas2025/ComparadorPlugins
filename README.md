# ComparadorPlugins 🔌

A comprehensive Python application for comparing plugin and theme versions between [weadown.com](https://weadown.com/) and [pluginswp.online](http://pluginswp.online). The tool automatically scrapes both websites, identifies version differences, sends email notifications, and provides both CLI and web interfaces for monitoring and control.

## Features

- 🔍 **Automated Scraping**: Retrieves plugin/theme data from both weadown.com and pluginswp.online
- 📊 **Version Comparison**: Identifies differences between the two sources
- 📧 **Email Notifications**: Sends detailed reports via SMTP with download URLs
- 💾 **History Persistence**: Stores comparison results in SQLite database
- 🖥️ **CLI Interface**: Command-line tools for running and managing comparisons
- 🌐 **Web UI**: Beautiful Flask-based interface for viewing history and controlling runs
- ⏰ **Scheduled Runs**: Daily automated comparisons using APScheduler
- 🔐 **Secure Configuration**: SMTP credentials managed via .env file

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. **Clone the repository**:
```bash
git clone https://github.com/Navas2025/ComparadorPlugins.git
cd ComparadorPlugins
```

2. **Create a virtual environment** (recommended):
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## Configuration

1. **Create your .env file**:
```bash
cp .env.example .env
```

2. **Edit the .env file** with your settings:

```env
# SMTP Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com
SMTP_TO=recipient@example.com

# Application Configuration
FLASK_PORT=5000
DATABASE_PATH=./data/comparisons.db
SCHEDULE_ENABLED=true
SCHEDULE_HOUR=9
SCHEDULE_MINUTE=0
```

### SMTP Configuration Notes

- **For Gmail**: 
  - Use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password
  - Enable 2-factor authentication first
  - Go to Google Account → Security → App Passwords to generate one

- **For other providers**: 
  - Check your email provider's SMTP settings
  - Common ports: 587 (TLS), 465 (SSL), 25 (unsecured)

## Usage

### Command Line Interface (CLI)

The CLI provides quick access to run comparisons and check status:

#### Run a comparison immediately:
```bash
python cli.py run
```

#### Check current status:
```bash
python cli.py status
```

#### View configuration:
```bash
python cli.py config
```

### Web Interface

The web interface provides a visual dashboard for managing comparisons and viewing history.

#### Start the web server:
```bash
python web_app.py
```

The web interface will be available at: **http://localhost:5000**

#### Features of the Web UI:
- ✅ View all comparison history
- ✅ Start/stop comparison runs
- ✅ View detailed differences for each comparison
- ✅ See download URLs for plugins with version differences
- ✅ Monitor current running status
- ✅ Check SMTP configuration status
- ✅ View scheduled run information

### Scheduled Runs

The application includes a built-in scheduler that runs comparisons automatically:

1. **Enable scheduling** in your .env file:
```env
SCHEDULE_ENABLED=true
SCHEDULE_HOUR=9
SCHEDULE_MINUTE=0
```

2. **Start the web server** (scheduler runs in background):
```bash
python web_app.py
```

The scheduler will automatically run comparisons at the specified time each day while the web server is running.

## Project Structure

```
ComparadorPlugins/
├── src/
│   ├── app.py              # Main application logic
│   ├── config.py           # Configuration management
│   ├── database.py         # SQLite database operations
│   ├── scraper.py          # Web scrapers for both sites
│   ├── comparator.py       # Version comparison logic
│   └── email_notifier.py   # SMTP email notifications
├── templates/
│   └── index.html          # Web UI template
├── static/                 # Static assets (if needed)
├── data/                   # Database storage (auto-created)
├── cli.py                  # Command-line interface
├── web_app.py             # Flask web application
├── requirements.txt        # Python dependencies
├── .env.example           # Configuration template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## How It Works

1. **Scraping**: The application scrapes plugin/theme listings from both weadown.com and pluginswp.online
2. **Comparison**: It compares versions between the two sources to identify differences
3. **Storage**: Results are stored in a SQLite database for history tracking
4. **Notification**: If differences are found, an email is sent with:
   - Plugin/theme names
   - Version from each source
   - Download URLs from weadown.com
5. **Scheduling**: Optionally runs automatically once per day

## Email Notification Format

When differences are found, you'll receive an email containing:

- **Subject**: Plugin Version Differences - YYYY-MM-DD
- **Content**: 
  - Summary of total differences found
  - Table with plugin names, versions from both sources
  - Direct download links from weadown.com
  - Timestamp of the comparison

## Database

The application uses SQLite for storing comparison history. The database includes:

- **comparisons** table: Records of each comparison run
- **differences** table: Detailed differences found in each run

Database location is configurable via the `DATABASE_PATH` environment variable (default: `./data/comparisons.db`).

## Troubleshooting

### Email not sending
- Verify SMTP credentials in .env file
- For Gmail, ensure you're using an App Password
- Check that your email provider allows SMTP connections
- Run `python cli.py config` to verify configuration

### Web UI not loading
- Ensure Flask is installed: `pip install flask`
- Check that port 5000 is not in use
- Try a different port in .env: `FLASK_PORT=8000`

### No plugins found
- The websites may have changed their structure
- Check the scrapers in `src/scraper.py` may need updates
- Verify internet connectivity
- Check logs for specific error messages

### Permission errors
- Ensure the `data/` directory has write permissions
- On Linux/Mac: `chmod 755 data/`

## Development

### Adding custom scrapers
Edit `src/scraper.py` to customize scraping logic for different website structures.

### Customizing email templates
Edit `src/email_notifier.py` to modify the email format.

### Changing schedule frequency
Modify the scheduler configuration in `web_app.py` or use environment variables.

## Security

- ⚠️ **Never commit your .env file** to version control
- ✅ Use App Passwords instead of regular passwords
- ✅ Keep your dependencies updated: `pip install --upgrade -r requirements.txt`
- ✅ The .gitignore file is configured to exclude sensitive files

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is provided as-is for educational and personal use.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Note**: This tool is designed for personal use. Please respect the terms of service of the websites being scraped and ensure you have permission to scrape their content.
