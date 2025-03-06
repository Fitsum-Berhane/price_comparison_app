from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, Profile, RetailerProfile, SavedProduct, SearchHistory

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Role'), {'fields': ('role',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'city', 'country')
    search_fields = ('user__email', 'first_name', 'last_name', 'city', 'country')

@admin.register(RetailerProfile)
class RetailerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'business_name', 'business_city', 'business_country', 'average_rating', 'is_verified')
    search_fields = ('user__email', 'business_name', 'business_city', 'business_country')
    list_filter = ('is_verified',)

@admin.register(SavedProduct)
class SavedProductAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    search_fields = ('user__email', 'product__name')
    list_filter = ('created_at',)

@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'query', 'product_clicked', 'created_at')
    search_fields = ('user__email', 'query', 'product_clicked__name')
    list_filter = ('created_at',)