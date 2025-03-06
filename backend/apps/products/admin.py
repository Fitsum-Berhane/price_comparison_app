from django.contrib import admin
from .models import (
    Category, Brand, Product, ProductImage, ProductSpecification,
    Retailer, RetailerProductPrice, PriceHistory
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'website')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1

class RetailerProductPriceInline(admin.TabularInline):
    model = RetailerProductPrice
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'lowest_price', 'highest_price', 'view_count')
    list_filter = ('brand', 'category')
    search_fields = ('name', 'description', 'sku', 'upc', 'mpn')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('lowest_price', 'highest_price', 'average_price', 'view_count')
    inlines = [ProductImageInline, ProductSpecificationInline, RetailerProductPriceInline]

@admin.register(Retailer)
class RetailerAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'is_scrapable', 'has_api', 'average_rating')
    list_filter = ('is_scrapable', 'has_api')
    search_fields = ('name', 'description', 'website')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(RetailerProductPrice)
class RetailerProductPriceAdmin(admin.ModelAdmin):
    list_display = ('product', 'get_retailer_name', 'price', 'currency', 'is_available', 'last_checked')
    list_filter = ('currency', 'is_available', 'is_free_shipping', 'last_checked')
    search_fields = ('product__name', 'retailer__name', 'small_retailer__business_name')
    
    def get_retailer_name(self, obj):
        if obj.retailer:
            return obj.retailer.name
        elif obj.small_retailer:
            return obj.small_retailer.business_name
        return "Unknown"
    get_retailer_name.short_description = 'Retailer'

@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'get_retailer_name', 'price', 'currency', 'timestamp')
    list_filter = ('timestamp', 'currency')
    search_fields = ('product__name', 'retailer__name', 'small_retailer__business_name')
    
    def get_retailer_name(self, obj):
        if obj.retailer:
            return obj.retailer.name
        elif obj.small_retailer:
            return obj.small_retailer.business_name
        return "Unknown"
    get_retailer_name.short_description = 'Retailer'