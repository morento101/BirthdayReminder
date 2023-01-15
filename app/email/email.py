from asgiref.sync import async_to_sync
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

from app.core.config import BASE_DIR, settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=BASE_DIR / 'templates'
)


async def send_birthday_reminder(email_to: str, content: dict):
    message = MessageSchema(
        subject='Birthday Reminder',
        recipients=[email_to],
        template_body=content,
        subtype='html',
    )

    fm = FastMail(conf)
    await fm.send_message(
        message, template_name='email/birthday_reminder.html'
    )
