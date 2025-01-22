import time

from django.conf import settings
from django.db import IntegrityError, models


class Job(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    )

    @classmethod
    def generate_job_id(cls, max_retries=3):
        for _ in range(max_retries):
            timestamp = int(time.time() * 1000)
            job_id = f"{settings.APP_NAME}_{timestamp}"
            if not cls.objects.filter(job_id=job_id).exists():
                return job_id
            time.sleep(0.001)

        raise IntegrityError("Could not generate unique job ID")

    id = models.CharField(
        primary_key=True, default=generate_job_id, max_length=100, editable=False
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    result = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
