from rest_framework import viewsets, generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Property, CustomUser, Booking, Review, SearchHistory, PropertyView
from .serializers import (
    PropertySerializer, RegisterSerializer, LoginSerializer,
    BookingSerializer, ReviewSerializer, SearchHistorySerializer,
    PropertyViewSerializer, GroupSerializer, UserSerializer
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.contrib.auth.models import Group
from rest_framework import status
from django.utils import timezone
from rest_framework import serializers


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save()
        group_name = self.request.data.get('group')
        if group_name:
            group_instance = Group.objects.get(name=group_name)
            user.groups.add(group_instance)
        else:
            default_group = Group.objects.get(name='Tenant')
            user.groups.add(default_group)


class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        # Создаем ответ с токенами
        response = Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })

        # Сохраняем access токен в куки
        response.set_cookie(
            key='access_token',
            value=str(refresh.access_token),
            httponly=True,  # Защита от доступа через JavaScript
            secure=False,  # Установите True для HTTPS в production
            samesite='Lax',  # Защита от CSRF в браузере
        )

        return response


class IsLandlord(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_landlord


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = {
        'price': ['gte', 'lte'],
        'location': ['exact', 'icontains'],
        'num_rooms': ['gte', 'lte'],
        'property_type': ['exact'],
    }
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at', 'views_count']

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
        property = serializer.validated_data['property']
        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']

        if Booking.objects.filter(property=property, start_date__lt=end_date, end_date__gt=start_date).exists():
            raise serializers.ValidationError("The selected dates overlap with an existing booking.")

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
        property = serializer.validated_data['property']
        if not Booking.objects.filter(property=property, user=self.request.user, end_date__lt=timezone.now()).exists():
            raise serializers.ValidationError("You can only review properties you've stayed at.")
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
