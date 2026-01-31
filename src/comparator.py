"""
Comparator module for finding differences between plugin versions.
"""
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PluginComparator:
    """Compare plugin versions between two sources."""
    
    def compare(self, weadown_plugins, pluginswp_plugins):
        """
        Compare plugins from both sources and return differences.
        
        Args:
            weadown_plugins: Dict of plugins from weadown.com
            pluginswp_plugins: Dict of plugins from pluginswp.online
            
        Returns:
            List of differences with download URLs
        """
        differences = []
        
        # Find common plugins
        weadown_names = set(weadown_plugins.keys())
        pluginswp_names = set(pluginswp_plugins.keys())
        
        common_plugins = weadown_names & pluginswp_names
        
        logger.info(f"Found {len(common_plugins)} common plugins to compare")
        logger.info(f"Weadown unique: {len(weadown_names - pluginswp_names)}")
        logger.info(f"Pluginswp unique: {len(pluginswp_names - weadown_names)}")
        
        # Compare versions of common plugins
        for plugin_name in common_plugins:
            weadown_data = weadown_plugins[plugin_name]
            pluginswp_data = pluginswp_plugins[plugin_name]
            
            weadown_version = weadown_data.get('version')
            pluginswp_version = pluginswp_data.get('version')
            
            # If both have versions and they differ
            if weadown_version and pluginswp_version and weadown_version != pluginswp_version:
                differences.append({
                    'name': plugin_name,
                    'weadown_version': weadown_version,
                    'pluginswp_version': pluginswp_version,
                    'download_url': weadown_data.get('download_url'),
                    'raw_title': weadown_data.get('raw_title')
                })
        
        # Also include plugins only in weadown (new plugins)
        only_in_weadown = weadown_names - pluginswp_names
        for plugin_name in only_in_weadown:
            weadown_data = weadown_plugins[plugin_name]
            differences.append({
                'name': plugin_name,
                'weadown_version': weadown_data.get('version'),
                'pluginswp_version': 'Not found',
                'download_url': weadown_data.get('download_url'),
                'raw_title': weadown_data.get('raw_title')
            })
        
        logger.info(f"Found {len(differences)} differences")
        return differences
