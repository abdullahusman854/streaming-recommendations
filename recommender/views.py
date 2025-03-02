# recommender/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Content, ContentSimilarity
from django.db.models import Q, F, ExpressionWrapper, FloatField
import numpy as np
from supabase import create_client, Client

class RecommendationsView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        content_type = request.query_params.get('content_type', 'movie')
        
        # Initialize Supabase client
        supabase: Client = create_client(
            '',
            ''
        )
        
        # Get user's watch history
        watch_history = supabase.table('Watching')\
            .select('*')\
            .eq('user', user_id)\
            .execute()
        
        if not watch_history.data:
            return Response({
            'recommendations': []
            })
        
        # Calculate content scores based on watch history
        return self.get_personalized_recommendations(
            watch_history.data, 
            content_type
        )

    def get_personalized_recommendations(self, watch_history, content_type):
        # Calculate weights for different factors
        watched_items = {}
        for item in watch_history:
            watched_items[item['tmdb_id']] = {
                'watch_progress': item['watch_progress'],
                'is_completed': item['is_completed']
            }

        # Get all content similar to watched content
        similar_content = ContentSimilarity.objects.filter(
            content__tmdb_id__in=watched_items.keys(),
            similar_content__content_type=content_type
        ).select_related('content', 'similar_content')

        # Calculate recommendation scores
        content_scores = {}
        for similarity in similar_content:
            watch_data = watched_items[similarity.content.tmdb_id]
            
            # Base score is the similarity score
            score = similarity.similarity_score
            
            # Adjust score based on watch progress
            if watch_data['is_completed']:
                score *= 1.2  # Boost score for completed content
            else:
                score *= (0.5 + float(watch_data['watch_progress']))

            # Adjust score based on rating
            score *= (similarity.similar_content.rating / 10.0)

            content_id = similarity.similar_content.id
            if content_id in content_scores:
                content_scores[content_id] = max(content_scores[content_id], score)
            else:
                content_scores[content_id] = score

        # Get recommended content
        recommended_content = Content.objects.filter(
            id__in=content_scores.keys()
        ).exclude(
            tmdb_id__in=watched_items.keys()
        )

        # Sort content by calculated scores
        sorted_content = sorted(
            recommended_content,
            key=lambda x: content_scores[x.id],
            reverse=True
        )[:20]

        return Response({
            'recommendations': self.serialize_content(sorted_content)
        })

    def serialize_content(self, content_queryset):
        return [{
            'id': item.id,
            'tmdb_id': item.tmdb_id,
            'name': item.name,
            'poster': item.poster,
            'rating': item.rating,
            'genres': item.genres,
            'description': item.description,
            'content_type': item.content_type,
            'stream_id': item.stream_id,
        } for item in content_queryset]