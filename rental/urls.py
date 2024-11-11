from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PropertyViewSet, RegisterView, LoginView, BookingViewSet, ReviewViewSet, SearchHistoryViewSet, PropertyViewViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'properties', PropertyViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'properties/(?P<property_pk>\d+)/reviews', ReviewViewSet, basename='reviews')
router.register(r'search-history', SearchHistoryViewSet, basename='search-history')
router.register(r'property-views', PropertyViewViewSet, basename='property-views')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]

