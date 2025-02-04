import asyncio
import logging
from pathlib import Path
from tempfile import TemporaryDirectory

from adrf.decorators import api_view
from asgiref.sync import sync_to_async
from django.apps import apps
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from .inference import OcrEngine
from .models import Job
from .serializers import (
    DocumentSerializer,
    JobSerializer,
    MultipartSerializer,
    PathSerializer,
)
from .utils import extract_zip

logger = logging.getLogger(settings.APP_NAME)


async def process_path(
    job_id, input_path: Path, multi_files: bool, ocr_engine: OcrEngine
):
    job = await sync_to_async(Job.objects.get)(id=job_id)

    # Update status to processing
    job.status = "processing"
    await sync_to_async(job.save)()

    documents = []
    if input_path.is_dir():
        if multi_files:
            ocr_result = await sync_to_async(ocr_engine.ocr_document_multi)(
                input_path.as_posix()
            )
            documents.append(ocr_result.formatted_results)
        else:
            for f in input_path.glob("*"):
                ocr_result = await sync_to_async(ocr_engine.ocr_document)(f.as_posix())
                documents.append(ocr_result.formatted_results)

    else:
        ocr_result = await sync_to_async(ocr_engine.ocr_document)(input_path.as_posix())
        documents.append(ocr_result.formatted_results)

    # Update with result
    job.status = "completed"
    job.result = {
        "documents": documents,
        "message": "Processing completed successfully",
    }
    await sync_to_async(job.save)()


async def process_file(
    job_id, uploaded_file: UploadedFile, multi_files: bool, ocr_engine: OcrEngine
):
    with TemporaryDirectory() as tmp_dir:
        # Read file and unzip into temporary directory
        if uploaded_file.name.lower().endswith(".zip"):
            extract_zip(uploaded_file, tmp_dir)
            input_path = Path(tmp_dir)

        else:
            input_path = Path(tmp_dir) / uploaded_file.name
            with input_path.open("wb") as dest:
                for chunk in uploaded_file.chunks():
                    dest.write(chunk)

    await process_path(job_id, input_path, multi_files, ocr_engine)


# Create your views here.
@api_view(["POST"])
async def ocr_job(request: Request):
    start_time = asyncio.get_event_loop().time()
    logger.info(f"Starting ocr_job at {start_time}")
    if request.method != "POST":
        # Validate request here

        return Response(
            {"message": "Invalid request method"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    logger.info(f"ocr_job POST request received with data: {request.data}")

    ocr_engine = apps.get_app_config(settings.APP_NAME).ocr_engine
    logger.info(
        f"Got OCR engine at {asyncio.get_event_loop().time() - start_time:.2f}s"
    )
    job = await sync_to_async(Job.objects.create)()
    job.result = {"message": "Processing started"}
    await sync_to_async(job.save)()
    logger.info(f"Created job at {asyncio.get_event_loop().time() - start_time:.2f}s")

    if "path" in request.data:
        request_serializer = PathSerializer(data=request.data)
        if not request_serializer.is_valid():
            job.result = request_serializer.error_messages
            job.status = "failed"
            await sync_to_async(job.save)()

            return Response(
                request_serializer.error_messages, status=status.HTTP_400_BAD_REQUEST
            )

        # Read in files
        input_path = Path(request_serializer.validated_data["path"])
        multiple_files = (
            input_path.is_dir() and not request_serializer.validated_data["single_file"]
        )
        logger.info(
            f"Validated path at {asyncio.get_event_loop().time() - start_time:.2f}s"
        )
        # Start processing in the background
        asyncio.create_task(
            process_path(job.id, input_path, multiple_files, ocr_engine)
        )
        logger.info(
            f"Created background task at {asyncio.get_event_loop().time() - start_time:.2f}s"
        )

        # Return the job ID immediately
        response_serializer = JobSerializer(job)
        logger.info(
            f"Prepared response at {asyncio.get_event_loop().time() - start_time:.2f}s"
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    request_serializer = MultipartSerializer(data=request.data)
    if not request_serializer.is_valid():
        job.result = request_serializer.error_messages
        job.status = "failed"
        await sync_to_async(job.save)()
        return Response(
            request_serializer.error_messages, status=status.HTTP_400_BAD_REQUEST
        )

    uploaded_file = request_serializer.validated_data["file"]

    # Start processing in the background
    asyncio.create_task(process_file(job.id, uploaded_file, False, ocr_engine))

    # Return the job ID immediately
    response_serializer = JobSerializer(job)

    return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
async def ocr_result(request: Request, job_id):
    logger.info(f"ocr_result GET request received with {job_id=}")

    try:
        job = await sync_to_async(Job.objects.get)(id=job_id)
        serializer = JobSerializer(job)
        return Response(serializer.data)
    except Job.DoesNotExist:
        return Response({"message": "Job not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
async def health_check(request):
    logger.info("Health check request")
    return Response({"status": "healthy"}, status=status.HTTP_200_OK)
