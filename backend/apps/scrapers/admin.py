from django.contrib import admin
from .models import ScraperConfig, ScraperRun, ScrapedProduct, UserAgent, ProxyServer

@admin.register(ScraperConfig)
class ScraperConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'retailer', 'scraper_type', 'is_active', 'last_run_status', 'last_run_time')
    list_filter = ('scraper_type', 'is_active')
    search_fields = ('name', 'retailer__name')

@admin.register(ScraperRun)
class ScraperRunAdmin(admin.ModelAdmin):
    list_display = ('scraper_config', 'start_time', 'end_time', 'status', 'products_scraped', 'updated_prices')
    list_filter = ('status', 'start_time')
    search_fields = ('scraper_config__name',)

@admin.register(ScrapedProduct)
class ScrapedProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'currency', 'is_processed', 'created_at')
    list_filter = ('is_processed', 'currency', 'created_at')
    search_fields = ('product_name', 'product_url')

@admin.register(UserAgent)
class UserAgentAdmin(admin.ModelAdmin):
    list_display = ('user_agent', 'description', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('user_agent', 'description')

@admin.register(ProxyServer)
class ProxyServerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'country', 'latency', 'is_active', 'is_working', 'last_checked')
    list_filter = ('protocol', 'is_active', 'is_working', 'country')
    search_fields = ('host', 'country')