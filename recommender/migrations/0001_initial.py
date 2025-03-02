# Generated by Django 5.1.4 on 2024-12-17 15:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tmdb_id', models.CharField(max_length=100, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('content_type', models.CharField(max_length=10)),
                ('stream_id', models.IntegerField(null=True)),
                ('rating', models.FloatField(null=True)),
                ('genres', models.JSONField(default=list)),
                ('cast', models.JSONField(default=list)),
                ('director', models.CharField(max_length=255, null=True)),
                ('category_id', models.CharField(max_length=100)),
                ('description', models.TextField(null=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'indexes': [models.Index(fields=['tmdb_id'], name='recommender_tmdb_id_e9338d_idx'), models.Index(fields=['content_type'], name='recommender_content_404f3c_idx')],
            },
        ),
        migrations.CreateModel(
            name='ContentSimilarity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('similarity_score', models.FloatField()),
                ('content', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='similarities', to='recommender.content')),
                ('similar_content', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recommender.content')),
            ],
            options={
                'unique_together': {('content', 'similar_content')},
            },
        ),
    ]
