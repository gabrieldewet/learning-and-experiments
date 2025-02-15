import uuid

from django.db import models


class WatchlistItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    movie_name = models.CharField(max_length=200)
    genre = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    watched = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.movie_name
