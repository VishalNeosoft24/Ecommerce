# admin_panel/tasks.py
from background_task import background
from django.core.mail import send_mail


@background(schedule=0)
def send_email_task(subject, plain_message, from_email, to, html_message):
    send_mail(
        subject,
        plain_message,
        from_email,
        [to],
        html_message=html_message,
    )
