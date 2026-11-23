from celery import Celery

from src.config import Config
from src.mail import mail, create_message

from asgiref.sync import async_to_sync


c_app = Celery("bookly")


c_app.conf.update(
    broker_url=Config.CELERY_BROKER_URL,
    result_backend=Config.CELERY_RESULT_BACKEND,

    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    timezone="Asia/Kolkata",
    enable_utc=True,

    # Monitoring configuration
    worker_send_task_events=True,
    task_send_sent_event=True,
    task_track_started=True,
)


@c_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=10
)
def send_email(self, recipients, subject, body):

    try:

        message = create_message(
            recipient=recipients,
            subject=subject,
            body=body
        )

        async_to_sync(mail.send_message)(message)

        return "Email sent successfully"

    except Exception as exc:

        raise self.retry(exc=exc)