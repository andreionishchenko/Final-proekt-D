from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, Property, Booking, Review, SearchHistory, PropertyView
from django.contrib.auth.models import Group

CustomUser = get_user_model()  # Получаем кастомную модель пользователя

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser  # Используем кастомную модель пользователя
        fields = ('email', 'username', 'password', 'is_landlord', 'is_tenant')  # Поля модели CustomUser
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Создаем пользователя с кастомной моделью
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            is_landlord=validated_data.get('is_landlord', False),
            is_tenant=validated_data.get('is_tenant', True)
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user = UserSerializer(read_only=True)  # Дополнительное поле для передачи информации о пользователе

    def validate(self, data):
        email = data['email']
        password = data['password']

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        if not user.check_password(password):
            raise serializers.ValidationError("Incorrect password.")

        refresh = RefreshToken.for_user(user)
        return {
            'user': UserSerializer(user).data,  # Возвращаем информацию о пользователе
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'description', 'location', 'price', 'num_rooms',
            'property_type', 'is_active', 'available', 'created_at'
        ]
        read_only_fields = ['created_at']


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'id', 'property', 'user', 'start_date', 'end_date', 'status', 'created_at'
        ]
        read_only_fields = ['user', 'status', 'created_at']

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError("End date must be after start date.")

        return data


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'property', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = ['id', 'user', 'keyword', 'created_at']
        read_only_fields = ['user', 'created_at']


class PropertyViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyView
        fields = ['id', 'user', 'property', 'viewed_at']
        read_only_fields = ['user', 'viewed_at']
