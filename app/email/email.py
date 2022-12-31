from asgiref.sync import async_to_sync
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

from app.core.config import BASE_DIR, settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.EMAIL_USERNAME,
    MAIL_PASSWORD=settings.EMAIL_PASSWORD,
    MAIL_FROM=settings.EMAIL_USERNAME,
    MAIL_PORT=settings.EMAIL_PORT,
    MAIL_SERVER=settings.EMAIL_HOST,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=BASE_DIR / 'templates'
)


@async_to_sync
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
