from rest_framework import generics, filters, permissions
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Category, Brand, Product, Retailer, PriceHistory
from .serializers import (
    CategorySerializer, BrandSerializer, ProductListSerializer, 
    ProductDetailSerializer, RetailerSerializer, PriceHistorySerializer
)
from .tasks import increment_view_count
from apps.accounts.models import SearchHistory


class CategoryListView(generics.ListAPIView):
    """List all categories."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['parent']


class CategoryDetailView(generics.RetrieveAPIView):
    """Retrieve a specific category."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class BrandListView(generics.ListAPIView):
    """List all brands."""
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class BrandDetailView(generics.RetrieveAPIView):
    """Retrieve a specific brand."""
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class ProductListView(generics.ListAPIView):
    """List all products with filtering and sorting."""
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'brand']
    search_fields = ['name', 'description', 'brand__name', 'category__name']
    ordering_fields = ['name', 'lowest_price', 'highest_price', 'created_at', 'view_count']
    ordering = ['name']


class ProductDetailView(generics.RetrieveAPIView):
    """Retrieve a specific product with detailed information."""
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Track view count asynchronously
        increment_view_count.delay(instance.id)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ProductSearchView(generics.ListAPIView):
    """Search products with advanced filtering."""
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'brand__name', 'category__name', 'specifications__value']
    ordering_fields = ['name', 'lowest_price', 'highest_price', 'view_count']
    ordering = ['name']
    
    def get_queryset(self):
        queryset = Product.objects.all()
        
        # Price range filtering
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(lowest_price__gte=float(min_price))
        if max_price:
            queryset = queryset.filter(lowest_price__lte=float(max_price))
        
        # Category filtering (supports multiple categories)
        categories = self.request.query_params.getlist('category')
        if categories:
            queryset = queryset.filter(category__slug__in=categories)
        
        # Brand filtering (supports multiple brands)
        brands = self.request.query_params.getlist('brand')
        if brands:
            queryset = queryset.filter(brand__slug__in=brands)
        
        # Track search if authenticated
        search_query = self.request.query_params.get('search')
        if search_query and self.request.user.is_authenticated:
            SearchHistory.objects.create(
                user=self.request.user,
                query=search_query
            )
        
        return queryset


class ProductPriceHistoryView(generics.ListAPIView):
    """Retrieve price history for a specific product."""
    serializer_class = PriceHistorySerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        product_slug = self.kwargs['slug']
        return PriceHistory.objects.filter(product__slug=product_slug).order_by('-timestamp')


class RetailerListView(generics.ListAPIView):
    """List all retailers."""
    queryset = Retailer.objects.all()
    serializer_class = RetailerSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']


class RetailerDetailView(generics.RetrieveAPIView):
    """Retrieve a specific retailer."""
    queryset = Retailer.objects.all()
    serializer_class = RetailerSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'