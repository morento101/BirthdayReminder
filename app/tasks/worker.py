from celery import Celery
from celery.schedules import solar

from app.core.config import settings
from app.email.email import send_birthday_reminder
from app.tasks.utils import (get_all_today_birthdays,
                             get_user_data_from_birthday)

celery = Celery(__name__)
celery.conf.timezone = 'Europe/Kiev'
celery.conf.enable_utc = True
celery.conf.broker_url = settings.CELERY_BROKER_URL
celery.conf.result_backend = settings.CELERY_RESULT_BACKEND


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60, create_task.s())


celery.conf.beat_schedule = {
    'add-at-melbourne-sunset': {
        'task': 'create_task',
        'schedule': solar('solar_noon', 50.450001, 30.523333),
        'args': (),
    },
}


@celery.task(name="create_task")
def create_task():
    birthdays = get_all_today_birthdays()

    for birthday in birthdays:
        user = get_user_data_from_birthday(birthday)

        send_birthday_reminder(
            user.email,
            {
                "subject": "Birthday Reminder",
                "user_name": user.username,
                "name_of_birthday_boy": birthday.name_of_birthday_boy,
                "descrition": birthday.description
            }
        )
