from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from .models import Product, PriceHistory

@shared_task
def update_product_prices():
    """Update price statistics for all products."""
    products = Product.objects.all()
    for product in products:
        product.update_price_stats()
    return f"Updated price statistics for {products.count()} products."

@shared_task
def increment_view_count(product_id):
    """Increment view count for a product."""
    try:
        product = Product.objects.get(id=product_id)
        product.view_count += 1
        product.save(update_fields=['view_count'])
        return f"Incremented view count for product {product.name}."
    except Product.DoesNotExist:
        return f"Product with ID {product_id} does not exist."

@shared_task
def clean_old_price_data():
    """Delete price history older than one year."""
    one_year_ago = timezone.now() - timedelta(days=365)
    old_records = PriceHistory.objects.filter(timestamp__lt=one_year_ago)
    count = old_records.count()
    old_records.delete()
    return f"Deleted {count} price history records older than one year."