"""
Models for the accounts app - handles users, profiles, and retailer accounts.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class UserManager(BaseUserManager):
    """Custom user manager for the User model."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with email and password."""
        if not email:
            raise ValueError(_('Users must have an email address'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model with email as the username field."""
    
    ROLE_CHOICES = (
        ('shopper', 'Shopper'),
        ('retailer', 'Retailer'),
        ('admin', 'Admin'),
    )
    
    username = None  # Remove username field
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='shopper')
    
    # Use email as the username field for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    def __str__(self):
        return self.email


class Profile(models.Model):
    """User profile model for additional user information."""
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=50, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email}'s Profile"


class RetailerProfile(models.Model):
    """Retailer profile for retailer-specific information."""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='retailer_profile', 
        limit_choices_to={'role': 'retailer'}
    )
    business_name = models.CharField(max_length=100)
    business_description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='retailer_logos/', blank=True, null=True)
    
    # Business address
    business_address = models.TextField()
    business_city = models.CharField(max_length=50)
    business_state = models.CharField(max_length=50)
    business_zip_code = models.CharField(max_length=10)
    business_country = models.CharField(max_length=50)
    
    # Business contact
    business_email = models.EmailField()
    business_phone = models.CharField(max_length=20)
    
    # Verification status
    is_verified = models.BooleanField(default=False)
    verification_notes = models.TextField(blank=True)
    
    # Rating (calculated from user reviews)
    average_rating = models.FloatField(default=0.0)
    rating_count = models.PositiveIntegerField(default=0)
    
    # API Integration (if available)
    has_api = models.BooleanField(default=False)
    api_endpoint = models.URLField(blank=True)
    api_key = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.business_name} (Retailer)"
    
    class Meta:
        verbose_name = "Retailer Profile"
        verbose_name_plural = "Retailer Profiles"


class SavedProduct(models.Model):
    """Model for users to save/bookmark products for later reference."""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_products')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'product')
        verbose_name = "Saved Product"
        verbose_name_plural = "Saved Products"
    
    def __str__(self):
        return f"{self.user.email} - {self.product.name}"


class SearchHistory(models.Model):
    """Model to track user search history for personalized recommendations."""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='search_history')
    query = models.CharField(max_length=255)
    product_clicked = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Search History"
        verbose_name_plural = "Search Histories"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.query}"