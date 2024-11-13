# rental/admin.py
from django.contrib import admin
from .models import CustomUser, Property, Booking, Review, SearchHistory, PropertyView
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'is_landlord', 'is_tenant', 'is_staff')
    search_fields = ('email', 'username')
    list_filter = ('is_landlord', 'is_tenant', 'is_staff')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Permissions', {'fields': ('is_landlord', 'is_tenant', 'is_staff', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_landlord', 'is_tenant'),
        }),
    )
    ordering = ('email',)

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'price', 'location', 'available', 'created_at')
    search_fields = ('title', 'location')
    list_filter = ('property_type', 'is_active', 'available')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {'fields': ('title', 'description', 'location', 'price', 'num_rooms', 'property_type', 'user')}),
        ('Availability', {'fields': ('is_active', 'available')}),
        ('Date Information', {'fields': ('created_at',)}),
    )
    readonly_fields = ('created_at',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('property', 'user', 'start_date', 'end_date', 'status', 'created_at')
    search_fields = ('property__title', 'user__email')
    list_filter = ('status', 'start_date', 'end_date')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('property', 'user', 'rating', 'created_at')
    search_fields = ('property__title', 'user__email')
    list_filter = ('rating',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'keyword', 'created_at')
    search_fields = ('user__email', 'keyword')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

@admin.register(PropertyView)
class PropertyViewAdmin(admin.ModelAdmin):
    list_display = ('user', 'property', 'viewed_at')
    search_fields = ('user__email', 'property__title')
    ordering = ('-viewed_at',)
    readonly_fields = ('viewed_at',)
