"""
Monkey patch to fix the cache timeout issue in Superset
This forces the Data Cache to use our configured timeout instead of any hardcoded values
"""

import logging
from superset.common import query_context_processor

logger = logging.getLogger(__name__)

# Store the original method
original_cache_timeout = query_context_processor.QueryContextProcessor.cache_timeout.fget

def patched_cache_timeout(self):
    """
    Patched cache_timeout that respects our configuration
    """
    # First check if there's a custom timeout from the query context
    if cache_timeout_rv := self._query_context.get_cache_timeout():
        logger.info(f"Using query context cache timeout: {cache_timeout_rv}")
        return cache_timeout_rv
    
    # Import here to avoid circular imports
    from flask import current_app
    
    # Check for our custom config variables first
    if chart_data_timeout := current_app.config.get("CHART_DATA_CACHE_TIMEOUT"):
        logger.info(f"Using CHART_DATA_CACHE_TIMEOUT: {chart_data_timeout}")
        return chart_data_timeout
        
    if data_cache_timeout := current_app.config.get("DATA_CACHE_TIMEOUT"):
        logger.info(f"Using DATA_CACHE_TIMEOUT: {data_cache_timeout}")
        return data_cache_timeout
    
    # Check DATA_CACHE_CONFIG
    if (
        data_cache_config_timeout := current_app.config.get("DATA_CACHE_CONFIG", {}).get(
            "CACHE_DEFAULT_TIMEOUT"
        )
    ):
        logger.info(f"Using DATA_CACHE_CONFIG timeout: {data_cache_config_timeout}")
        return data_cache_config_timeout
    
    # Fall back to global default
    default_timeout = current_app.config.get("CACHE_DEFAULT_TIMEOUT", 86400)
    logger.info(f"Using CACHE_DEFAULT_TIMEOUT: {default_timeout}")
    return default_timeout

# Apply the monkey patch
query_context_processor.QueryContextProcessor.cache_timeout = property(patched_cache_timeout)

logger.info("✅ Cache timeout patch applied successfully!")
print("🔧 Cache timeout monkey patch loaded - will respect configured timeouts")