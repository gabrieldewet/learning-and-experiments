import logging

from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

logger = logging.getLogger(settings.APP_NAME)


# Create your views here.
@api_view(["POST"])
def ocr_job(request: Request):
    if request.method != "POST":
        # Validate request here

        return Response({"message": "Invalid request method"})

    logger.debug(f"ocr_job POST request received with data: {request.data}")
    return Response({"message": "POST request received", "data": request.data})


@api_view(["GET"])
def ocr_result(request: Request, job_id):
    logger.debug(f"ocr_result GET request received with {job_id=}")
    return Response({"message": "GET request received", "job_id": job_id})
