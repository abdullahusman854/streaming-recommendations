# recommender/management/commands/verify_data.py

from django.core.management.base import BaseCommand
from recommender.models import Content, ContentSimilarity

class Command(BaseCommand):
    help = 'Verify content and similarity data in the database'

    def handle(self, *args, **kwargs):
        # Check Content table
        content_count = Content.objects.count()
        movie_count = Content.objects.filter(content_type='movie').count()
        series_count = Content.objects.filter(content_type='series').count()
        rejected_movies_count = Content.objects.filter(content_type='rejected_movie').count()
        
        self.stdout.write(f"Total content items: {content_count}")
        self.stdout.write(f"Movies: {movie_count+rejected_movies_count}")
        self.stdout.write(f"Reject Movies: {rejected_movies_count}")
        self.stdout.write(f"Series: {series_count}")
        