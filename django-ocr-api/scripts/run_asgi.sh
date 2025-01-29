# With uvicorn
uvicorn ocr_api.asgi:application --port 8001 --reload

# With gunicorn
# gunicorn -k uvicorn.workers.UvicornWorker ocr_api.asgi:application --bind :8001 --reload