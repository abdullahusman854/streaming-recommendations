# Generated by Django 5.1.4 on 2024-12-19 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0002_alter_content_category_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='poster',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
