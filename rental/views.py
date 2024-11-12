# rental/views.py
from rest_framework import viewsets, generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Property, CustomUser, Booking, Review, SearchHistory, PropertyView
from .serializers import PropertySerializer, RegisterSerializer, LoginSerializer, BookingSerializer, ReviewSerializer, SearchHistorySerializer, PropertyViewSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.contrib.auth.models import Group, User
from .serializers import GroupSerializer, UserSerializer
from rest_framework import status


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        group = self.request.data.get('group')
        if group:
            group_instance = Group.objects.get(name=group)
            user.groups.add(group_instance)
        else:
            default_group = Group.objects.get(name='Tenant')  # Группа по умолчанию
            user.groups.add(default_group)


class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)


class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)

class IsLandlord(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_landlord

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = {
        'price': ['gte', 'lte'],  # Минимальная и максимальная цена
        'location': ['exact', 'icontains'],  # Точный поиск и поиск по части строки
        'num_rooms': ['gte', 'lte'],  # Диапазон количества комнат
        'property_type': ['exact'],  # Тип жилья
    }
    search_fields = ['title', 'description']  # Поиск по заголовкам и описаниям
    ordering_fields = ['price', 'created_at', 'views_count', 'reviews__count']  # Сортировка по цене, дате добавления, количеству просмотров и количеству отзывов

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAuthenticated, IsLandlord]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super(PropertyViewSet, self).get_permissions()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def increment_view(self, request, pk=None):
        property = self.get_object()
        property.views_count += 1
        property.save()
        PropertyView.objects.create(user=request.user, property=property)
        return Response({'status': 'view count incremented'})

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    filterset_fields = {
        'property': ['exact'],
        'start_date': ['gte', 'lte'],
        'end_date': ['gte', 'lte'],
        'status': ['exact'],
    }
    ordering_fields = ['start_date', 'end_date', 'created_at']

    def get_queryset(self):
        if self.request.user.is_landlord:
            return self.queryset.filter(property__user=self.request.user)
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        booking = self.get_object()
        if request.user != booking.property.user:
            return Response({'detail': 'You do not have permission to confirm or cancel this booking.'}, status=403)

        serializer = self.get_serializer(booking, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        property_id = self.kwargs.get('property_pk')
        return self.queryset.filter(property_id=property_id)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SearchHistoryViewSet(viewsets.ModelViewSet):
    queryset = SearchHistory.objects.all()
    serializer_class = SearchHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



class PropertyViewViewSet(viewsets.ModelViewSet):
    queryset = PropertyView.objects.all()
    serializer_class = PropertyViewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
