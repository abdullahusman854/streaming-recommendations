# recommender/models.py

from django.db import models

class Content(models.Model):
    stream_id = models.IntegerField(unique=True, default=0)  # Added default value
    tmdb_id = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=20)  # 'movie' or 'series'
    poster = models.CharField(max_length=255, null=True)
    rating = models.FloatField(null=True)
    genres = models.JSONField(default=list)
    cast = models.JSONField(default=list)
    director = models.CharField(max_length=255, null=True)
    category_id = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['stream_id']),
            models.Index(fields=['content_type']),
        ]

class ContentSimilarity(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='similarities')
    similar_content = models.ForeignKey(Content, on_delete=models.CASCADE)
    similarity_score = models.FloatField()

    class Meta:
        unique_together = ('content', 'similar_content')