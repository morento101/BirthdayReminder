from celery import Celery

from app.core.config import settings
from app.email.email import send_birthday_reminder

celery = Celery(__name__)
celery.conf.broker_url = settings.CELERY_BROKER_URL
celery.conf.result_backend = settings.CELERY_RESULT_BACKEND


@celery.task(name="create_task")
def create_task():
    send_birthday_reminder(
        'tlcees@gmail.com',
        {
            "subject": "hi",
            "user_name": "John",
            "name_of_birthday_boy": "Anton",
            "descrition": "no note"
        }
    )
