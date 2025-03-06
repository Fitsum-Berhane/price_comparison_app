"""
Models for the products app - handles products, categories, and pricing.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify


User = get_user_model()


class Category(models.Model):
    """Product category model."""
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Generate slug from name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Brand(models.Model):
    """Product brand model."""
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    website = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Generate slug from name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Product model - the core of the price comparison system."""
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True)
    description = models.TextField(blank=True)
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    
    # Main product image
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    # Product attributes
    sku = models.CharField(max_length=100, blank=True)  # Stock Keeping Unit
    upc = models.CharField(max_length=30, blank=True)   # Universal Product Code
    mpn = models.CharField(max_length=100, blank=True)  # Manufacturer Part Number
    
    # Price information (calculated from retailer prices)
    lowest_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    highest_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    average_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Popularity and stats
    view_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Generate slug from name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def update_price_stats(self):
        """Update price statistics based on current retailer prices."""
        prices = self.retailer_prices.filter(is_available=True).values_list('price', flat=True)
        
        if prices:
            self.lowest_price = min(prices)
            self.highest_price = max(prices)
            self.average_price = sum(prices) / len(prices)
            self.save()


class ProductImage(models.Model):
    """Additional product images."""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', 'created_at']
    
    def __str__(self):
        return f"Image for {self.product.name}"


class ProductSpecification(models.Model):
    """Product specifications / features."""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications')
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=255)
    
    class Meta:
        unique_together = ('product', 'name')
    
    def __str__(self):
        return f"{self.product.name} - {self.name}: {self.value}"


class Retailer(models.Model):
    """
    Retailer model for major retailers.
    For small business retailers, use RetailerProfile from accounts app.
    """
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    website = models.URLField()
    
    # For scraping configurations
    is_scrapable = models.BooleanField(default=True)
    scraper_class = models.CharField(max_length=100, blank=True)
    
    # For API configurations
    has_api = models.BooleanField(default=False)
    api_endpoint = models.URLField(blank=True)
    
    # General info
    logo = models.ImageField(upload_to='retailers/', blank=True, null=True)
    description = models.TextField(blank=True)
    
    # Ratings
    average_rating = models.FloatField(default=0.0)
    rating_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Generate slug from name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class RetailerProductPrice(models.Model):
    """Product prices from different retailers."""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='retailer_prices')
    
    # Can be either a major retailer or a small business retailer
    retailer = models.ForeignKey(Retailer, on_delete=models.CASCADE, related_name='product_prices', null=True, blank=True)
    small_retailer = models.ForeignKey('accounts.RetailerProfile', on_delete=models.CASCADE, related_name='product_prices', null=True, blank=True)
    
    # Must have either retailer or small_retailer (but not both)
    
    # Price information
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Shipping information
    shipping_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    is_free_shipping = models.BooleanField(default=False)
    
    # Product URL at the retailer
    product_url = models.URLField()
    
    # Stock information
    is_available = models.BooleanField(default=True)
    stock_status = models.CharField(max_length=50, blank=True)  # e.g., 'In Stock', 'Out of Stock', '5 Left'
    
    # Previous price (for tracking price changes)
    previous_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_updated_at = models.DateTimeField(auto_now=True)
    
    # When was this last verified/scraped
    last_checked = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [
            ('product', 'retailer'),
            ('product', 'small_retailer'),
        ]
        verbose_name = "Retailer Product Price"
        verbose_name_plural = "Retailer Product Prices"
    
    def __str__(self):
        retailer_name = self.retailer.name if self.retailer else self.small_retailer.business_name
        return f"{self.product.name} - {retailer_name}: {self.price} {self.currency}"
    
    def save(self, *args, **kwargs):
        # Track price changes
        if self.pk:
            old_instance = RetailerProductPrice.objects.get(pk=self.pk)
            if old_instance.price != self.price:
                self.previous_price = old_instance.price
        
        super().save(*args, **kwargs)
        
        # Update product's price statistics
        self.product.update_price_stats()


class PriceHistory(models.Model):
    """Historical price data for analytics and price tracking."""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history')
    retailer = models.ForeignKey(Retailer, on_delete=models.CASCADE, related_name='price_history', null=True, blank=True)
    small_retailer = models.ForeignKey('accounts.RetailerProfile', on_delete=models.CASCADE, related_name='price_history', null=True, blank=True)
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Price History"
        verbose_name_plural = "Price Histories"
        ordering = ['-timestamp']
    
    def __str__(self):
        retailer_name = self.retailer.name if self.retailer else self.small_retailer.business_name
        return f"{self.product.name} - {retailer_name}: {self.price} {self.currency} on {self.timestamp.date()}"