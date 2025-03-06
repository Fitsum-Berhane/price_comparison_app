from rest_framework import serializers
from .models import (
    Category, Brand, Product, ProductImage, ProductSpecification,
    Retailer, RetailerProductPrice, PriceHistory
)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'parent', 'image')


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'name', 'slug', 'description', 'logo', 'website')


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'alt_text', 'is_primary')


class ProductSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpecification
        fields = ('id', 'name', 'value')


class RetailerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Retailer
        fields = ('id', 'name', 'slug', 'website', 'logo', 'description', 'average_rating', 'rating_count')


class RetailerProductPriceSerializer(serializers.ModelSerializer):
    retailer = RetailerSerializer(read_only=True)
    
    class Meta:
        model = RetailerProductPrice
        fields = (
            'id', 'retailer', 'small_retailer', 'price', 'currency',
            'shipping_cost', 'is_free_shipping', 'product_url',
            'is_available', 'stock_status', 'last_checked'
        )


class PriceHistorySerializer(serializers.ModelSerializer):
    retailer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PriceHistory
        fields = ('id', 'retailer_name', 'price', 'currency', 'timestamp')
    
    def get_retailer_name(self, obj):
        if obj.retailer:
            return obj.retailer.name
        elif obj.small_retailer:
            return obj.small_retailer.business_name
        return None


class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'category', 'brand', 'image', 'lowest_price', 'highest_price')


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    additional_images = ProductImageSerializer(many=True, read_only=True)
    specifications = ProductSpecificationSerializer(many=True, read_only=True)
    retailer_prices = RetailerProductPriceSerializer(many=True, read_only=True)
    price_history = PriceHistorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'description', 'category', 'brand',
            'image', 'sku', 'upc', 'mpn', 'lowest_price', 'highest_price',
            'average_price', 'additional_images', 'specifications',
            'retailer_prices', 'price_history', 'view_count', 'created_at'
        )


class ProductSerializer(serializers.ModelSerializer):
    """Simple serializer for use in other app serializers."""
    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'image', 'lowest_price')