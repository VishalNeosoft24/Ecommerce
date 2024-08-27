# Django imports
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.template import Template, Context

# Local imports
from .tasks import send_email_task


def send_admin_reply_email(user, user_query, admin_reply, template):
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
    from_email = "vishal.prajapati@neosoftmail.com"
    to = user.email

    send_email_task(
        template.subject,
        plain_message,
        from_email,
        to,
        html_message=html_message,
    )
