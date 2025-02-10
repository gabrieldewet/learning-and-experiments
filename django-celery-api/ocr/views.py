import logging
import time
from pathlib import Path

from celery import chain
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from .models import File, Job
from .serializers import (
    JobSerializer,
    MultipartSerializer,
    PathSerializer,
)
from .tasks import process_file_task, process_path_task

logger = logging.getLogger(settings.APP_NAME)


# Create your views here.
@api_view(["POST"])
def ocr_job(request: Request):
    start_time = time.time()
    logger.info(f"Starting ocr_job at {start_time}")
    if request.method != "POST":
        return Response(
            {"message": "Invalid request method"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    logger.info(f"ocr_job POST request received with data: {request.data}")

    job = Job.objects.create()
    job.save()

    logger.info(f"Created job at {time.time() - start_time:.2f}s")

    if "file" in request.data:
        request_serializer = MultipartSerializer(data=request.data)
        if not request_serializer.is_valid():
            job.result = request_serializer.error_messages
            job.status = "failed"
            job.save()
            return Response(request_serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = request_serializer.validated_data["file"]
        job.multi_doc = request_serializer.validated_data["single_file"]
        job.save()

        # Start processing in the background
        # Create a Celery chain
        task_chain = chain(process_file_task.s(job_id=job.id, upload=uploaded_file), process_path_task.s())
        task_chain.apply_async()
        logger.info(f"Created background task for {job.id=} at {time.time() - start_time:.2f}s")
        response_serializer = JobSerializer(job)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    request_serializer = PathSerializer(data=request.data)
    if not request_serializer.is_valid():
        job.result = request_serializer.error_messages
        job.status = "failed"
        job.save()
        return Response(request_serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)

    # Read in files
    input_path = Path(request_serializer.validated_data["path"])
    job.multi_doc = input_path.is_dir() and not request_serializer.validated_data["single_file"]
    job.save()

    logger.info(f"Validated path at {time.time() - start_time:.2f}s")

    # Start processing in the background
    process_path_task.delay(job.id)
    logger.info(f"Created background task for {job.id=} at {time.time() - start_time:.2f}s")

    # Return the job ID immediately
    response_serializer = JobSerializer(job)
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def ocr_result(request: Request, job_id):
    logger.info(f"ocr_result GET request received with {job_id=}")

    try:
        job = Job.objects.get(id=job_id)
        serializer = JobSerializer(job)
        return Response(serializer.data)
    except Job.DoesNotExist:
        return Response({"message": "Job not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
def health_check(request):
    logger.info("Health check request")
    return Response({"status": "healthy"}, status=status.HTTP_200_OK)
