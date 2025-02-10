import logging
import os
from pathlib import Path

from celery import shared_task
from celery.contrib.abortable import AbortableTask
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile

from .inference import OcrEngine
from .models import Job
from .utils import extract_zip

logger = logging.getLogger(settings.APP_NAME)


# Task class to load models
class MLTask(AbortableTask):
    """
    Base task class that combines model loading with Celery's AbortableTask.
    """

    abstract = True

    def __init__(self):
        super().__init__()
        self.ocr_engine = None

    def __call__(self, *args, **kwargs):
        if not self.ocr_engine:
            logging.info("Loading OCR Engine...")
            self.ocr_engine = OcrEngine()
            logging.info("OCR Model loaded")
        return self.run(*args, **kwargs)


@shared_task(bind=True, base=MLTask)
def process_path_task(self: MLTask, job_id: str):
    """Celery task to process a path."""
    logger.info(f"Request: {self.request!r}")

    job = Job.objects.get(id=job_id)
    input_path = Path(job.file_path)
    logger.info(f"{job_id=} | {job.file_path=} | {job.multi_doc=}")

    # Update status to processing
    job.status = "processing"
    job.save()

    documents = []
    if input_path.is_dir():
        if job.multi_doc:
            ocr_result = self.ocr_engine.ocr_document_multi(input_path.as_posix())
            documents.append(ocr_result.formatted_results)
        else:
            for f in input_path.glob("*"):
                ocr_result = self.ocr_engine.ocr_document(f.as_posix())
                documents.append(ocr_result.formatted_results)

    else:
        ocr_result = self.ocr_engine.ocr_document(input_path.as_posix())
        documents.append(ocr_result.formatted_results)

    # Update with result
    job.status = "completed"
    job.result = {
        "documents": documents,
        "message": "Processing completed successfully",
    }
    job.save()


@shared_task(bind=True, base=AbortableTask)
def process_file_task(self: AbortableTask, job_id: str, uploaded_file: UploadedFile):
    logger.info(f"Request: {self.request!r}")
    job = Job.objects.get(id=job_id)
    job.status = "extracting"
    job.save()

    # Filename
    extract_path = os.path.join(settings.MEDIA_ROOT, "uploaded_files")
    os.makedirs(extract_path, exist_ok=True)

    if uploaded_file.name.lower().endswith(".zip"):
        extract_zip(uploaded_file, extract_path)

    else:
        with open(f"{extract_path}/uploaded_file.name", "wb") as dest:
            for chunk in uploaded_file.chunks():
                dest.write(chunk)

    process_path_task.delay(job_id, input_path.as_posix(), multi_files)
