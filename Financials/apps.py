from django.apps import AppConfig


class FinancialsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Financials'

    def ready(self):
        from . import signals
