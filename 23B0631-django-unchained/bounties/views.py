from django.shortcuts import render
from django.core.cache import cache
from django.contrib.auth.models import User
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, ScopedRateThrottle, UserRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import Bounty
from .serializers import UserRegisterSerializer, BountySerializer

class RegisterView(generics.CreateAPIView):
    """
    Register a new user in the town's ledger.
    """
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle, ScopedRateThrottle]
    throttle_scope = 'burst'


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Login endpoint exchanging username and password for a JWT token pair.
    """
    throttle_classes = [AnonRateThrottle, ScopedRateThrottle]
    throttle_scope = 'burst'


class CustomTokenRefreshView(TokenRefreshView):
    """
    Refresh endpoint exchanging refresh token for a new access token.
    """
    throttle_classes = [AnonRateThrottle, ScopedRateThrottle]
    throttle_scope = 'burst'


class BountyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling CRUD operations on Bounties.
    Restricts access to only the owner's bounties.
    Caches read operations and invalidates cache on write operations.
    """
    serializer_class = BountySerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get_queryset(self):
        # Enforce that users can only retrieve/query their own bounties.
        # This prevents ID enumeration/harvesting attacks by returning 404.
        return Bounty.objects.filter(owner=self.request.user)

    def list(self, request, *args, **kwargs):
        # Query-specific cache key per user
        cache_key = f"user_{request.user.id}_bounties_list"
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        # Cache data for 5 minutes (300 seconds)
        cache.set(cache_key, data, timeout=300)
        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        bounty_id = kwargs.get('pk')
        cache_key = f"user_{request.user.id}_bounty_{bounty_id}"
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        # get_object() automatically queries get_queryset(), enforcing ownership
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        # Cache the detail response for 5 minutes (300 seconds)
        cache.set(cache_key, data, timeout=300)
        return Response(data)

    def perform_create(self, serializer):
        # Automatically assign ownership of the new bounty to the requesting user
        bounty = serializer.save(owner=self.request.user)
        self.clear_user_cache(self.request.user.id, bounty.id)

    def perform_update(self, serializer):
        bounty = serializer.save()
        self.clear_user_cache(self.request.user.id, bounty.id)

    def perform_destroy(self, instance):
        owner_id = instance.owner.id
        bounty_id = instance.id
        instance.delete()
        self.clear_user_cache(owner_id, bounty_id)

    def clear_user_cache(self, user_id, bounty_id=None):
        # Clear the list cache key for the user
        list_cache_key = f"user_{user_id}_bounties_list"
        cache.delete(list_cache_key)

        # Clear the specific detail cache key if a bounty ID is provided
        if bounty_id is not None:
            detail_cache_key = f"user_{user_id}_bounty_{bounty_id}"
            cache.delete(detail_cache_key)
