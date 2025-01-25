import asyncio
import logging

from asgiref.sync import sync_to_async
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Job
from .serializers import JobSerializer

logger = logging.getLogger(settings.APP_NAME)


async def process_job(job_id):
    """Simulate some async processing"""
    job = await sync_to_async(Job.objects.get)(id=job_id)

    # Update status to processing
    job.status = "processing"
    await sync_to_async(job.save)()

    # Simulate some work
    await asyncio.sleep(10)

    # Update with result
    job.status = "completed"
    job.result = {"message": "Processing completed successfully"}
    await sync_to_async(job.save)()


# Create your views here.
@api_view(["POST"])
async def ocr_job(request: Request):
    if request.method != "POST":
        # Validate request here

        return Response({"message": "Invalid request method"})

    # Create a new job
    job = await sync_to_async(Job.objects.create)()

    # Start processing in the background
    asyncio.create_task(process_job(job.id))

    logger.debug(f"ocr_job POST request received with data: {request.data}")
    return Response({"message": "POST request received", "data": request.data})


@api_view(["GET"])
async def ocr_result(request: Request, job_id):
    logger.debug(f"ocr_result GET request received with {job_id=}")
    return Response({"message": "GET request received", "job_id": job_id})
