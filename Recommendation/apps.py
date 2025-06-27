from django.apps import AppConfig


class RecommendationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Recommendation'

    def ready(self):
        from .utils import get_sbert_model
        get_sbert_model()
