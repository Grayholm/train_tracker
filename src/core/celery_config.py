from celery import Celery

from src.core.config import settings

celery_app = Celery(main="lkeep", broker=settings.redis_settings.redis_url, backend=settings.redis_settings.redis_url)

celery_app.autodiscover_tasks(packages=["src.core"])