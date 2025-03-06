from celery import shared_task
import importlib
import logging
from datetime import datetime
import random
from django.utils import timezone

from .models import ScraperConfig, ScraperRun, UserAgent, ProxyServer
from apps.products.models import Retailer, RetailerProductPrice, PriceHistory, Product

# Set up logging
logger = logging.getLogger(__name__)

@shared_task
def run_scraper(config_id):
    """Run a specific scraper based on its configuration ID."""
    try:
        config = ScraperConfig.objects.get(id=config_id, is_active=True)
    except ScraperConfig.DoesNotExist:
        logger.error(f"Scraper configuration with ID {config_id} not found or not active.")