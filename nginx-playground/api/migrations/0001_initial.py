# Generated by Django 5.1.6 on 2025-02-24 21:06

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WatchlistItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('movie_name', models.CharField(max_length=200)),
                ('genre', models.CharField(max_length=100)),
                ('notes', models.TextField(blank=True)),
                ('watched', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
