# This file is needed to make the directory a Python package
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def api_base_url() -> str:
    """
    Get the base URL for the Academic Analyzer API from settings
    with improved error handling and logging.
    """
    base_url = getattr(settings, "ACADEMIC_ANALYZER_BASE_URL", None)
    
    if not base_url:
        # Log a warning if no URL is configured
        logger.warning("ACADEMIC_ANALYZER_BASE_URL not configured in settings, using default")
        base_url = "http://localhost:5000"
    
    # Log the API base URL being used
    logger.debug(f"Using Academic Analyzer API base URL: {base_url}")
    return base_url.rstrip("/")