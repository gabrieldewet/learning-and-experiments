import asyncio
import logging

from adrf.decorators import api_view
from asgiref.sync import sync_to_async
from django.apps import apps
from django.conf import settings
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from .inference import OcrEngine
from .models import Job
from .serializers import JobSerializer, MultipartSerializer, PathSerializer

logger = logging.getLogger(settings.APP_NAME)


async def process_job(job_id, ocr_engine: OcrEngine):
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

        return Response(
            {"message": "Invalid request method"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    logger.info(f"ocr_job POST request received with data: {request.data}")

    ocr_engine = apps.get_app_config(settings.APP_NAME).ocr_engine

    if "path" in request.data:
        serializer = PathSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.error_messages, status=status.HTTP_400_BAD_REQUEST
            )

        # Read in files

        job = Job.objects.create(status="pending")
        process_prediction.delay(path=serializer.validated_data["path"], job_id=job.id)
        return Response(JobSerializer(job).data)

    # Create a new job
    job = await sync_to_async(Job.objects.create)()
    job.result = {"message": "Processing started"}

    # Start processing in the background
    asyncio.create_task(process_job(job.id))

    # Return the job ID immediately
    serializer = JobSerializer(job)

    return Response(serializer.data, status=status.HTTP_201_CREATED)
    # return Response({"message": "POST request received", "data": request.data})


@api_view(["GET"])
async def ocr_result(request: Request, job_id):
    logger.info(f"ocr_result GET request received with {job_id=}")

    try:
        job = await sync_to_async(Job.objects.get)(id=job_id)
        serializer = JobSerializer(job)
        return Response(serializer.data)
    except Job.DoesNotExist:
        serializer = ErrorMesageSerializer({"message": "Job not found"})
        return Response(serializer.data, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
async def health_check(request):
    logger.info("Health check request")
    return Response({"status": "healthy"}, status=status.HTTP_200_OK)
