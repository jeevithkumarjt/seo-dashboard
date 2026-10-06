from celery import Celery
from os import getenv
celery=Celery("seo_worker",broker=getenv("REDIS_URL","redis://redis:6379/0"),
              backend=getenv("REDIS_URL","redis://redis:6379/0"))
celery.conf.task_routes={"app.tasks.*":{"queue":"seo"}}
