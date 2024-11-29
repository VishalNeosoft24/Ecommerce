# orders/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from order_management.models import UserOrder
from django.utils import timezone
from django.utils.html import strip_tags
from django.template import Template, Context
from admin_panel.models import EmailTemplate
from order_management.models import UserWishList
from datetime import timedelta
from collections import defaultdict


@shared_task
def send_daily_order_summary():
    """Send Daily Order Summary"""
    today = timezone.localtime().date()
    orders = UserOrder.objects.filter(created_at__date=today)

    subject = f"Daily Order Summary for {today}"
    template = EmailTemplate.objects.filter(title="Daily Order Summary").first()
    context = {"orders": orders, "today_date": today}
    rendered_content = Template(template.content).render(Context(context))
    plain_message = strip_tags(rendered_content)

    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [settings.DEFAULT_FROM_EMAIL],
        html_message=rendered_content,
        fail_silently=False,
    )


@shared_task
def send_weekly_wishlist_summary():
    """Send Weekly Wishlist Summary"""
    last_week = timezone.now() - timedelta(days=70)
    wishlist_items = UserWishList.objects.filter(created_at__gte=last_week)

    # Initialize a regular dictionary to hold user wishlist data
    user_wishlist = {}

    for item in wishlist_items:
        product_details = {
            "name": item.product.name,
            "price": item.product.price,
        }

        # Check if the user's wishlist already exists in the dictionary
        if item.user.username not in user_wishlist:
            user_wishlist[item.user.username] = (
                []
            )  # Initialize the list if it doesn't exist

        # Append the product details to the user's wishlist
        user_wishlist[item.user.username].append(product_details)

    # # Initialize a defaultdict to hold user wishlist data
    # user_wishlist = defaultdict(list)

    # for item in wishlist_items:
    #     product_details = {
    #         "name": item.product.name,
    #         "price": item.product.price,
    #     }
    #     user_wishlist[item.user.username].append(product_details)

    # user_wishlist = dict(user_wishlist)

    if wishlist_items.exists():
        subject = "Weekly User Wish List Summary"
        context = {"user_wishlist": user_wishlist}
        template = EmailTemplate.objects.filter(
            title="Weekly Wish List Summary"
        ).first()
        rendered_content = Template(template.content).render(Context(context))
        plain_message = strip_tags(rendered_content)

        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            html_message=rendered_content,
            fail_silently=False,
        )
