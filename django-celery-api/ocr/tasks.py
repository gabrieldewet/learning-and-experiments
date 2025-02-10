import logging
import os
import zipfile
from io import BytesIO
from pathlib import Path

from celery import shared_task
from celery.contrib.abortable import AbortableTask
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile

from .inference import OcrEngine
from .models import File, Job

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
    files = job.files.all()  # Get all related MyFile instances
    logger.info(f"{job_id=} | {len(files)=} | {job.multi_doc=}")

    # Update status to processing
    job.status = "processing"
    job.save()

    documents = []
    if len(files) > 1:
        if job.multi_doc:
            ocr_result = self.ocr_engine.ocr_document_multi(Path(files[0].file.path).parent.as_posix())
            documents.append(ocr_result.formatted_results)
        else:
            for f in files:
                ocr_result = self.ocr_engine.ocr_document(f.file.path)
                documents.append(ocr_result.formatted_results)

    else:
        ocr_result = self.ocr_engine.ocr_document(files[0].file.path)
        documents.append(ocr_result.formatted_results)

    # Update with result
    job.status = "completed"
    job.result = {
        "documents": documents,
        "message": "Processing completed successfully",
    }
    job.save()


@shared_task(bind=True, base=AbortableTask)
def process_file_task(self: AbortableTask, job_id: str, upload: UploadedFile):
    logger.info(f"Request: {self.request!r}")
    job = Job.objects.get(id=job_id)
    job.status = "extracting"
    job.save()

    logger.info(f"{job_id=} | {job.multi_doc=}")

    if upload.name.lower().endswith(".zip"):
        with zipfile.ZipFile(BytesIO(upload)) as zip_file:
            for file_info in zip_file.infolist():
                # Skip directories
                if file_info.is_dir():
                    continue

                file_name = file_info.filename
                with zip_file.open(file_info) as extracted_file:
                    # Create a MyFile instance and save the file
                    uploaded_file = File(job=job)
                    uploaded_file.file.save(file_name, ContentFile(extracted_file.read()))
                    uploaded_file.save()

    else:
        uploaded_file = File(job=job)
        uploaded_file.file.save(upload.name, ContentFile(upload))
        uploaded_file.save()

    uploaded_files = [f.file.name for f in job.files.all()]
    logger.info(f"Saved file(s)\n{'\n\t'.join(uploaded_files)}\n to {job.id=}")
    return job.id
