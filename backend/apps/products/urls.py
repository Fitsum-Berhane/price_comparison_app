from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    
    # Brands
    path('brands/', views.BrandListView.as_view(), name='brand_list'),
    path('brands/<slug:slug>/', views.BrandDetailView.as_view(), name='brand_detail'),
    
    # Products
    path('', views.ProductListView.as_view(), name='product_list'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # Search
    path('search/', views.ProductSearchView.as_view(), name='product_search'),
    
    # Price history
    path('<slug:slug>/price-history/', views.ProductPriceHistoryView.as_view(), name='price_history'),
    
    # Retailers
    path('retailers/', views.RetailerListView.as_view(), name='retailer_list'),
    path('retailers/<slug:slug>/', views.RetailerDetailView.as_view(), name='retailer_detail'),
]