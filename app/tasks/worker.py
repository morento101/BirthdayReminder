from asgiref.sync import async_to_sync
from celery import Celery

from app.core.config import settings
from app.tasks.utils import get_all_today_birthdays

celery = Celery(__name__)
celery.conf.broker_url = settings.CELERY_BROKER_URL
celery.conf.result_backend = settings.CELERY_RESULT_BACKEND


@celery.task(name="create_task")
def create_task():
    pass

    # birthdays = async_to_sync(get_all_today_birthdays)()

    # for birthday in birthdays:

    #     contents = [

    #     ]
