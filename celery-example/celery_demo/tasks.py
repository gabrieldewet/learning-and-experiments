import time

from celery_demo.celery import app


@app.task
def add(x, y):
    time.sleep(5)
    return x + y
