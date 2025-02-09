from celery import Celery

app = Celery(
    "celery_demo", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0", include=["celery_demo.tasks"]
)

if __name__ == "__main__":
    app.start()
