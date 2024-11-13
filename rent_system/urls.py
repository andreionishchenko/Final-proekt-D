# rent_system/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('rental.urls')),  # Подключение всех маршрутов из rental/urls.py
]
