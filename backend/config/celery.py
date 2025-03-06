"""
Celery configuration for handling background tasks.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create the Celery app
app = Celery('price_comparison')

# Configure Celery using Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

# Define periodic tasks
app.conf.beat_schedule = {
    'update-prices-daily': {
        'task': 'apps.scrapers.tasks.update_all_prices',
        'schedule': crontab(hour=0, minute=0),  # Run at midnight every day
    },
    'update-recommendations-weekly': {
        'task': 'apps.recommendations.tasks.update_recommendations',
        'schedule': crontab(day_of_week=0, hour=1, minute=0),  # Run at 1 AM every Sunday
    },
    'clean-old-price-data-monthly': {
        'task': 'apps.products.tasks.clean_old_price_data',
        'schedule': crontab(day_of_month=1, hour=2, minute=0),  # Run at 2 AM on the 1st of every month
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')