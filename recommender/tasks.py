# recommender/tasks.py

from celery import shared_task
from .content_manager import ContentManager, RecommendationEngine

@shared_task
def update_content_cache():
    manager = ContentManager()
    manager.update_content_cache()

@shared_task
def update_recommendations():
    engine = RecommendationEngine()
    engine.calculate_similarities()