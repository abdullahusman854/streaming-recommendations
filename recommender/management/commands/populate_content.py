# recommender/management/commands/populate_content.py

from django.core.management.base import BaseCommand
from recommender.content_manager import ContentManager, RecommendationEngine
from recommender.models import Content

class Command(BaseCommand):
    help = 'Populate initial content data and calculate similarities'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting movie population process...")
        
        # Update content
        manager = ContentManager()
        manager.update_content()
        # Then calculate and store similarities
        engine = RecommendationEngine()
        engine.calculate_similarities()
        
        self.stdout.write(self.style.SUCCESS('Successfully populated calculated similarities'))