import random

from celery_demo.tasks import add


def run_n_tasks(n: int = 5):
    for i in range(n):
        task = add.delay(random.random(), random.random())

        print(f"{task=}")
