"""
Email notification module for sending comparison results via SMTP.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailNotifier:
    """Send email notifications for plugin version differences."""
    
    def __init__(self, config):
        """Initialize with SMTP configuration."""
        self.config = config
    
    def send_differences(self, differences):
        """
        Send an email with the list of differences.
        
        Args:
            differences: List of plugin differences to report
        """
        if not differences:
            logger.info("No differences to send")
            return
        
        if not self.config.is_configured():
            logger.warning("SMTP not configured, skipping email")
            return
        
        try:
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'Plugin Version Differences - {datetime.now().strftime("%Y-%m-%d")}'
            msg['From'] = self.config.SMTP_FROM
            msg['To'] = self.config.SMTP_TO
            
            # Create email body
            text_body = self._create_text_body(differences)
            html_body = self._create_html_body(differences)
            
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.config.SMTP_HOST, self.config.SMTP_PORT) as server:
                server.starttls()
                server.login(self.config.SMTP_USERNAME, self.config.SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully with {len(differences)} differences")
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise
    
    def _create_text_body(self, differences):
        """Create plain text email body."""
        body = f"Plugin/Theme Version Differences Report\n"
        body += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        body += f"Total Differences: {len(differences)}\n\n"
        body += "=" * 70 + "\n\n"
        
        for diff in differences:
            body += f"Plugin: {diff['name']}\n"
            body += f"  Weadown Version: {diff.get('weadown_version', 'N/A')}\n"
            body += f"  Pluginswp Version: {diff.get('pluginswp_version', 'N/A')}\n"
            if diff.get('download_url'):
                body += f"  Download URL: {diff['download_url']}\n"
            body += "\n"
        
        return body
    
    def _create_html_body(self, differences):
        """Create HTML email body."""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .header {{ background-color: #4CAF50; color: white; padding: 10px; }}
                .footer {{ margin-top: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>Plugin/Theme Version Differences Report</h2>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Total Differences: {len(differences)}</p>
            </div>
            
            <table>
                <tr>
                    <th>Plugin Name</th>
                    <th>Weadown Version</th>
                    <th>Pluginswp Version</th>
                    <th>Download URL</th>
                </tr>
        """
        
        for diff in differences:
            download_link = ''
            if diff.get('download_url'):
                download_link = f'<a href="{diff["download_url"]}">Download</a>'
            
            html += f"""
                <tr>
                    <td>{diff['name']}</td>
                    <td>{diff.get('weadown_version', 'N/A')}</td>
                    <td>{diff.get('pluginswp_version', 'N/A')}</td>
                    <td>{download_link}</td>
                </tr>
            """
        
        html += """
            </table>
            
            <div class="footer">
                <p>This is an automated report from Plugin Comparator</p>
            </div>
        </body>
        </html>
        """
        
        return html
