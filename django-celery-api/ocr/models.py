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
        ("aborted", "Aborted"),
    )

    id = models.CharField(primary_key=True, default=generate_job_id, max_length=100, editable=False)
    task_id = models.CharField(max_length=30, null=True, blank=True)
    multi_doc = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    result = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class File(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to="uploaded_files/")  # Relative to MEDIA_ROOT
    description = models.CharField(max_length=255, blank=True)  # Optional description

    def __str__(self):
        return self.file.name
