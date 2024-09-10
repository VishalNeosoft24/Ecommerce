# Django imports
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.template import Template, Context

from django.conf import settings

# Local imports
from .tasks import send_email_task


def send_admin_reply_email(user, user_query, admin_reply, template):
    """
    Sends an email to the user with the admin's reply.

    Renders an email template with the provided context, which includes
    the user, user query, admin reply, and the email template content.
    The rendered content is then embedded in a base email template.

    Args:
        user (User): The user to whom the email will be sent.
        user_query (str): The query or message from the user.
        admin_reply (str): The reply from the admin.
        template (EmailTemplate): The email template to use for rendering the message.

    Returns:
        None: Sends an email using the provided `send_email_task` function.
    """

    # Create the context for rendering the template
    context = {
        "user": user,
        "user_query": user_query,
        "admin_reply": admin_reply,
        "template_content": template.content,
    }

    # Render the template content with the context
    rendered_content = Template(template.content).render(Context(context))

    # Pass the rendered content to your base email template
    html_message = render_to_string(
        "admin_panel/base_email_template.html",
        {
            "rendered_content": rendered_content,
            "current_year": timezone.now().year,
        },
    )
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    to = user.email

    send_email_task(
        template.subject,
        plain_message,
        from_email,
        to,
        html_message=html_message,
    )


def send_user_credentials_email(user, password):
    """
    Sends an email to the user with their account credentials.

    Renders an email template with the user's credentials and login URL.
    The rendered content is used to create the email body, which is sent
    to the user.

    Args:
        user (User): The user to whom the email will be sent.
        password (str): The user's password.

    Returns:
        None: Sends an email using the provided `send_email_task` function.
    """

    subject = "Your Account Credentials"
    login_url = "http://127.0.0.1:8000/admin-panel/login/"
    context = {
        "user": user,
        "password": password,
        "login_url": login_url,
    }
    html_message = render_to_string("admin_panel/user_credentials_email.html", context)
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email

    send_email_task(
        subject,
        plain_message,
        from_email,
        to_email,
        html_message=html_message,
    )
