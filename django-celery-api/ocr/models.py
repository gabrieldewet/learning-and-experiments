import time

from django.conf import settings
from django.db import models


def generate_job_id():
    """Generate a job ID combining app label and timestamp"""
    timestamp = int(time.time() * 1000)
    return f"{settings.APP_NAME}_{timestamp}"


class Job(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("extracting", "Extracting"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    )

    id = models.CharField(primary_key=True, default=generate_job_id, max_length=100, editable=False)
    file = models.FileField(upload_to="uploaded_files/")
    multi_doc = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    result = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
