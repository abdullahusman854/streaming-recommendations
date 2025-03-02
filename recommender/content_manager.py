# recommender/content_manager.py

import requests
from django.conf import settings
from .models import Content, ContentSimilarity
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ContentManager:
    def __init__(self):
        self.base_url = settings.IPTV_SETTINGS['BASE_URL']
        self.username = settings.IPTV_SETTINGS['USERNAME']
        self.password = settings.IPTV_SETTINGS['PASSWORD']

    def sync_to_database(self, movies, series, rejected_movies=None):
        # Handle rejected movies first
        if rejected_movies:
            for movie_id in rejected_movies:
                Content.objects.update_or_create(
                    stream_id=movie_id,  # Changed from tmdb_id to stream_id
                    defaults={
                        'name': '',
                        'content_type': 'rejected_movie',
                        'tmdb_id': None,
                        'poster': '',
                        'rating': 0.0,
                        'genres': [],
                        'cast': [],
                        'director': '',
                        'category_id': '',
                        'description': ''
                    }
                )

        # Process movies
        for movie in movies:
            try:
                # Safely convert rating to float
                rating = 0.0
                if movie.get('rating'):
                    try:
                        rating = float(movie.get('rating'))
                    except (ValueError, TypeError):
                        rating = 0.0
                
                # Safely handle genres and cast
                genres = movie.get('genre', '').split(',') if movie.get('genre') else []
                genres = [g.strip() for g in genres if g.strip()]
                
                cast = movie.get('cast', '').split(',') if movie.get('cast') else []
                cast = [c.strip() for c in cast if c.strip()]
                
                Content.objects.update_or_create(
                    stream_id=movie.get('stream_id'),  # Changed from tmdb_id to stream_id
                    defaults={
                        'tmdb_id': str(movie.get('tmdb_id')),
                        'name': movie.get('name', ''),
                        'content_type': 'movie',
                        'poster': movie.get('stream_icon'),
                        'rating': rating,
                        'genres': genres,
                        'cast': cast,
                        'director': movie.get('director', ''),
                        'category_id': movie.get('category_id', ''),
                        'description': movie.get('description', '')
                    }
                )
            except Exception as e:
                print(f"Error processing movie {movie.get('stream_id')}: {e}")
                continue
        
        # Process series
        for series_item in series:
            try:
                # Safely convert rating to float
                rating = 0.0
                if series_item.get('rating'):
                    try:
                        rating = float(series_item.get('rating'))
                    except (ValueError, TypeError):
                        rating = 0.0
                
                # Safely handle genres
                genres = series_item.get('genre', '').split('/') if series_item.get('genre') else []
                genres = [g.strip() for g in genres if g.strip()]
                
                Content.objects.update_or_create(
                    stream_id=series_item.get('series_id'),  # Changed from tmdb_id to stream_id
                    defaults={
                        'tmdb_id': str(series_item.get('tmdb')),
                        'name': series_item.get('name', ''),
                        'content_type': 'series',
                        'poster': series_item.get('cover'),
                        'rating': rating,
                        'genres': genres,
                        'cast': [],
                        'director': '',
                        'category_id': series_item.get('category_id', ''),
                        'description': series_item.get('plot', '')
                    }
                )
            except Exception as e:
                print(f"Error processing series {series_item.get('series_id')}: {e}")
                continue

    def update_content(self):
        try:
            # Get existing stream IDs from database (including rejected movies)
            existing_stream_ids = set(Content.objects.filter(
                content_type__in=['movie', 'rejected_movie']
            ).values_list('stream_id', flat=True))

            # Fetch new movies
            new_movies = self.fetch_all_movies()
            processed_movies = []
            rejected_movies = []
            count = 0
            for movie in new_movies[:50]:
                try:
                    if movie['stream_id'] not in existing_stream_ids:
                        movie_info = self.fetch_movie_info(movie['stream_id'])
                        if (
                            movie_info 
                            and isinstance(movie_info.get('info'), dict)
                            and 'name' in movie_info['info']
                            and 'genre' in movie_info['info']
                            and movie_info['info']['name']
                        ):
                            processed_movies.append({**movie, **movie_info['info']})
                        elif (not isinstance(movie_info.get('info'), dict)):
                            pass
                        else:
                            rejected_movies.append(movie['stream_id'])
                    count += 1
                    if count % 50 == 0:
                        print(f"{count} movies processed")
                except Exception as e:
                    print(f"Error fetching info for movie {movie['stream_id']}: {e}")

            series_data = self.fetch_all_series()
            
            # Update database with new content, including rejected movies
            if processed_movies or series_data or rejected_movies:
                self.sync_to_database(processed_movies, series_data, rejected_movies)

        except Exception as e:
            print(f"An error occurred while updating content: {e}")

    # Rest of the methods remain unchanged
    def fetch_movie_info(self, stream_id):
        url = f"{self.base_url}?username={self.username}&password={self.password}&action=get_vod_info&vod_id={stream_id}"
        response = requests.get(url)
        return response.json() if response.status_code == 200 else None

    def fetch_all_movies(self):
        url = f"{self.base_url}?username={self.username}&password={self.password}&action=get_vod_streams"
        response = requests.get(url)
        return response.json() if response.status_code == 200 else []

    def fetch_all_series(self):
        url = f"{self.base_url}?username={self.username}&password={self.password}&action=get_series"
        response = requests.get(url)
        return response.json() if response.status_code == 200 else []
    

class RecommendationEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')

    def prepare_content_features(self, content):
        features = []
        for item in content:
            # Combine all relevant features with appropriate weights
            name = item.name.lower() + " " + item.name.lower()  # Double weight for title
            genres = " ".join(item.genres) if item.genres else ""
            cast = " ".join(item.cast) if item.cast else ""
            director = item.director.lower() if item.director else ""
            description = item.description.lower() if item.description else ""
            
            feature_text = f"{name} {genres} {genres} {cast} {director} {description}"  # Double weight for genres
            features.append(feature_text)
        return features

    def calculate_similarities(self):
        # Calculate similarities separately for movies and series
        for content_type in ['movie', 'series']:
            content = Content.objects.filter(content_type=content_type)
            if not content.exists():
                continue
                
            features = self.prepare_content_features(content)
            if not features:
                continue
                
            tfidf_matrix = self.vectorizer.fit_transform(features)
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # Delete existing similarities for this content type
            ContentSimilarity.objects.filter(
                content__content_type=content_type
            ).delete()
            
            # Create new similarities
            similarities = []
            content_list = list(content)
            
            for idx, item in enumerate(content_list):
                # Get top 20 similar items
                similar_indices = similarity_matrix[idx].argsort()[:-21:-1]
                for similar_idx in similar_indices[1:]:  # Skip self-similarity
                    if similarity_matrix[idx][similar_idx] > 0.01:  # Only store meaningful similarities
                        similarities.append(
                            ContentSimilarity(
                                content=item,
                                similar_content=content_list[similar_idx],
                                similarity_score=float(similarity_matrix[idx][similar_idx])
                            )
                        )

            # Bulk create in batches to handle large datasets
            batch_size = 1000
            for i in range(0, len(similarities), batch_size):
                ContentSimilarity.objects.bulk_create(similarities[i:i+batch_size])