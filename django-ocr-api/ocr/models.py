from django.db import models


class OCRJob(models.Model):
    file_name = models.TextField()
    result = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
