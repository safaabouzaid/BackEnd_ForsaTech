from django.apps import AppConfig

class DevloperConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'devloper'

    def ready(self):
        import devloper.signals  

