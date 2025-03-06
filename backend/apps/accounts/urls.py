from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication views
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('retailer-profile/update/', views.RetailerProfileUpdateView.as_view(), name='retailer_profile_update'),
    
    # Saved products
    path('saved-products/', views.SavedProductListView.as_view(), name='saved_products'),
    path('saved-products/<int:product_id>/', views.SavedProductToggleView.as_view(), name='toggle_saved_product'),
    
    # Search history
    path('search-history/', views.SearchHistoryListView.as_view(), name='search_history'),
    path('search-history/<int:pk>/', views.SearchHistoryDeleteView.as_view(), name='delete_search_history'),
    path('search-history/clear/', views.SearchHistoryClearView.as_view(), name='clear_search_history'),
]