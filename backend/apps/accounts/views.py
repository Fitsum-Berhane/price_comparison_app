from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from .models import Profile, RetailerProfile, SavedProduct, SearchHistory
from .serializers import (
    UserCreateSerializer, UserSerializer, 
    ProfileUpdateSerializer, RetailerProfileUpdateSerializer,
    SavedProductSerializer, SearchHistorySerializer
)
from apps.products.models import Product

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """Register new users."""
    permission_classes = [permissions.AllowAny]
    serializer_class = UserCreateSerializer


class UserProfileView(generics.RetrieveAPIView):
    """Retrieve the current user's profile."""
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user


class ProfileUpdateView(generics.UpdateAPIView):
    """Update the current user's profile."""
    serializer_class = ProfileUpdateSerializer
    
    def get_object(self):
        return self.request.user.profile


class RetailerProfileUpdateView(generics.UpdateAPIView):
    """Update the current user's retailer profile."""
    serializer_class = RetailerProfileUpdateSerializer
    
    def get_object(self):
        if self.request.user.role != 'retailer':
            return Response(
                {"detail": "Only retailer accounts can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        return self.request.user.retailer_profile


class SavedProductListView(generics.ListAPIView):
    """List all saved products for the current user."""
    serializer_class = SavedProductSerializer
    
    def get_queryset(self):
        return SavedProduct.objects.filter(user=self.request.user)


class SavedProductToggleView(APIView):
    """Toggle saving/unsaving a product."""
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        saved_product, created = SavedProduct.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if not created:
            # If the product was already saved, delete it (unsave)
            saved_product.delete()
            return Response({"detail": "Product unsaved successfully."}, status=status.HTTP_200_OK)
        
        return Response(
            SavedProductSerializer(saved_product).data, 
            status=status.HTTP_201_CREATED
        )


class SearchHistoryListView(generics.ListAPIView):
    """List search history for the current user."""
    serializer_class = SearchHistorySerializer
    
    def get_queryset(self):
        return SearchHistory.objects.filter(user=self.request.user)


class SearchHistoryDeleteView(generics.DestroyAPIView):
    """Delete a specific search history entry."""
    
    def get_queryset(self):
        return SearchHistory.objects.filter(user=self.request.user)


class SearchHistoryClearView(APIView):
    """Clear all search history for the current user."""
    def delete(self, request):
        SearchHistory.objects.filter(user=request.user).delete()
        return Response({"detail": "Search history cleared."}, status=status.HTTP_204_NO_CONTENT)