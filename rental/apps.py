
from django.apps import AppConfig
class RentalConfig(AppConfig):
    name = 'rental'
    def ready(self):
        import rental.signals   # импортируем сигналы

