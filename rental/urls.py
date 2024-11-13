# rental/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PropertyViewSet, RegisterView, LoginView, BookingViewSet,
    ReviewViewSet, SearchHistoryViewSet, PropertyViewViewSet, GroupViewSet
)

router = DefaultRouter()
router.register(r'groups', GroupViewSet)
router.register(r'properties', PropertyViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'properties/(?P<property_pk>\d+)/reviews', ReviewViewSet, basename='property-reviews')
router.register(r'search-history', SearchHistoryViewSet, basename='search-history')
router.register(r'property-views', PropertyViewViewSet, basename='property-views')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('', include(router.urls)),  # Подключение всех маршрутов от router без дублирования
]
