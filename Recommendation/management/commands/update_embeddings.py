from django.core.management.base import BaseCommand
from Recommendation.tasks import generate_all_opportunity_embeddings

class Command(BaseCommand):
    help = "Generate or update embeddings for all opportunities"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting to update opportunity embeddings...")
        generate_all_opportunity_embeddings()
        self.stdout.write(self.style.SUCCESS("Successfully updated all opportunity embeddings."))
