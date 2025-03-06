"""
Models for the scrapers app - handles web scraping configurations.
"""

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.text import slugify


class ScraperConfig(models.Model):
    """Configuration settings for various retailer scrapers."""
    
    SCRAPER_TYPE_CHOICES = (
        ('html', 'HTML Scraper'),
        ('api', 'API Integration'),
        ('selenium', 'Selenium Scraper'),
    )
    
    retailer = models.OneToOneField('products.Retailer', on_delete=models.CASCADE, related_name='scraper_config')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    scraper_type = models.CharField(max_length=10, choices=SCRAPER_TYPE_CHOICES)
    
    # Base URL patterns
    base_url = models.URLField(help_text="Base URL of the retailer's website")
    product_url_pattern = models.CharField(
        max_length=255, 
        help_text="URL pattern for product pages (use {product_id} as placeholder)",
        blank=True
    )
    search_url_pattern = models.CharField(
        max_length=255, 
        help_text="URL pattern for search results (use {query} as placeholder)",
        blank=True
    )
    
    # Selectors for HTML scraping
    selectors = models.JSONField(default=dict, blank=True)
    
    # API configuration (if scraper_type is 'api')
    api_key = models.CharField(max_length=255, blank=True)
    api_secret = models.CharField(max_length=255, blank=True)
    api_endpoint = models.URLField(blank=True)
    api_parameters = models.JSONField(default=dict, blank=True)
    
    # Rate limiting settings
    request_delay = models.FloatField(
        default=1.0, 
        help_text="Delay between requests in seconds"
    )
    max_retries = models.PositiveIntegerField(default=3)
    
    # User agent rotation
    rotate_user_agents = models.BooleanField(default=False)
    use_proxy = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_run_status = models.CharField(max_length=50, blank=True)
    last_run_time = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Scraper Configuration"
        verbose_name_plural = "Scraper Configurations"
    
    def __str__(self):
        return f"{self.name} Scraper Config"
    
    def save(self, *args, **kwargs):
        """Generate slug from name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ScraperRun(models.Model):
    """Record of each scraper run, for monitoring and debugging."""
    
    STATUS_CHOICES = (
        ('success', 'Success'),
        ('partial', 'Partial Success'),
        ('failed', 'Failed'),
    )
    
    scraper_config = models.ForeignKey(ScraperConfig, on_delete=models.CASCADE, related_name='runs')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='failed')
    products_scraped = models.PositiveIntegerField(default=0)
    new_prices_found = models.PositiveIntegerField(default=0)
    updated_prices = models.PositiveIntegerField(default=0)
    errors = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Scraper Run"
        verbose_name_plural = "Scraper Runs"
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.scraper_config.name} Run - {self.start_time}"


class ScrapedProduct(models.Model):
    """Temporarily stores scraped product data before processing."""
    
    scraper_run = models.ForeignKey(ScraperRun, on_delete=models.CASCADE, related_name='scraped_products')
    
    # Raw data
    raw_data = models.JSONField()
    
    # Extracted data
    product_name = models.CharField(max_length=255)
    product_url = models.URLField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Optional data
    image_url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    sku = models.CharField(max_length=100, blank=True)
    upc = models.CharField(max_length=30, blank=True)
    availability = models.BooleanField(default=True)
    
    # Processing status
    is_processed = models.BooleanField(default=False)
    processing_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Scraped Product"
        verbose_name_plural = "Scraped Products"
    
    def __str__(self):
        return f"Scraped: {self.product_name} - {self.price} {self.currency}"


class UserAgent(models.Model):
    """Collection of user agents for rotation during scraping."""
    
    user_agent = models.CharField(max_length=500, unique=True)
    description = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "User Agent"
        verbose_name_plural = "User Agents"
    
    def __str__(self):
        return self.user_agent


class ProxyServer(models.Model):
    """Proxy servers for rotating IPs during scraping."""
    
    PROTOCOL_CHOICES = (
        ('http', 'HTTP'),
        ('https', 'HTTPS'),
        ('socks4', 'SOCKS4'),
        ('socks5', 'SOCKS5'),
    )
    
    protocol = models.CharField(max_length=6, choices=PROTOCOL_CHOICES)
    host = models.CharField(max_length=255)
    port = models.PositiveIntegerField()
    username = models.CharField(max_length=100, blank=True)
    password = models.CharField(max_length=100, blank=True)
    
    country = models.CharField(max_length=2, blank=True, help_text="ISO country code")
    latency = models.FloatField(null=True, blank=True, help_text="Average latency in milliseconds")
    
    is_active = models.BooleanField(default=True)
    last_checked = models.DateTimeField(null=True, blank=True)
    is_working = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Proxy Server"
        verbose_name_plural = "Proxy Servers"
        unique_together = ('protocol', 'host', 'port')
    
    def __str__(self):
        return f"{self.protocol}://{self.host}:{self.port}"