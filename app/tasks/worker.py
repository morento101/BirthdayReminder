from asgiref.sync import async_to_sync
from celery import Celery

from app.core.config import settings
from app.tasks.utils import get_all_today_birthdays
from app.email.email import send_birthday_reminder

celery = Celery(__name__)
celery.conf.broker_url = settings.CELERY_BROKER_URL
celery.conf.result_backend = settings.CELERY_RESULT_BACKEND


@celery.task(name="create_task")
def create_task():
    birthdays = get_all_today_birthdays()

    send_birthday_reminder('tlcees@gmail.com', {"subject": "hi"})
