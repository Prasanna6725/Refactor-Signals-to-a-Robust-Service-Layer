from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'

    def ready(self):
        # Signals were used initially but have been moved to a service layer.
        # If you need to enable legacy signals for experiments, import them here.
        # import orders.signals
        pass
