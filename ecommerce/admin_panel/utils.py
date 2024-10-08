# Django imports
import csv
import threading
from datetime import datetime
from io import BytesIO, StringIO
from django.db.models import DecimalField, IntegerField, FloatField
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.template import Template, Context

from django.conf import settings
from django.db.models import Count, F, Sum, Q, Value, ExpressionWrapper, Func
from django.core.paginator import Paginator
from django.db.models.functions import Coalesce
from django.core.mail import send_mail

from weasyprint import HTML

from admin_panel.models import Coupon
from user_management.models import User
from product_management.models import Product


def send_email_task(subject, plain_message, from_email, to, html_message):
    def send_email():
        send_mail(
            subject,
            plain_message,
            from_email,
            to,
            html_message=html_message,
        )

    # Create and start a new thread for sending the email
    email_thread = threading.Thread(target=send_email)
    email_thread.start()


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
        [to],
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
    if (
        user.is_superuser
        or user.groups.filter(name__in=["order_manager", "inventory_manager"]).exists()
    ):
        login_url = "http://127.0.0.1:8000/admin-panel/login/"
    else:
        login_url = "http://127.0.0.1:8000/login/"

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
        subject=subject,
        plain_message=plain_message,
        from_email=from_email,
        to=[to_email],
        html_message=html_message,
    )


def send_order_confirmation_email(customer_email, context, template):
    # Render the HTML template with context data

    # Render the template content with the context
    rendered_content = Template(template.content).render(Context(context))

    html_content = render_to_string(
        "customer_portal/order_confirmation_email.html",
        {
            "rendered_content": rendered_content,
        },
    )
    plain_message = strip_tags(html_content)  # Convert HTML to plain text

    # Prepare email details
    subject = f"Order Confirmation - {context['order_number']}"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = customer_email

    # Schedule the email sending task
    send_email_task(
        subject=subject,
        plain_message=plain_message,
        from_email=from_email,
        to=[to_email],
        html_message=html_content,
    )


class ReportExtraction:
    """Dynamic Report"""

    def __init__(self, request, report_name) -> None:
        """initialization"""
        self.request = request
        self.report_name = report_name

    def extract_filters(self):
        """Extract filters from request."""
        start_date = self.request.GET.get(
            "start_date", datetime.now().date().strftime("%Y-%m-01")
        )
        end_date = self.request.GET.get(
            "end_date", datetime.now().date().strftime("%Y-%m-%d")
        )
        search_value = self.request.GET.get("search", "")
        page = self.request.GET.get("page", 1)

        return start_date, end_date, search_value, page

    def generate_context(
        self, page_obj, table_headers, table_fields, start_date, end_date, search_value
    ):
        """Generate context for report views."""
        context = {
            "page_obj": page_obj,
            "table_headers": table_headers,
            "table_fields": table_fields,
            "start_date": start_date,
            "end_date": end_date,
            "search_value": search_value,
        }
        return context

    def sales_queryset(self, paginate=True):
        """Fetch products related to the sales report."""

        # Extract filters from request
        start_date, end_date, search_value, page = self.extract_filters()

        filters = {}
        if start_date:
            filters["order_details__order__created_at__date__gte"] = start_date
        if end_date:
            filters["order_details__order__created_at__date__lte"] = end_date

        sales_data = (
            Product.objects.filter(order_details__order__isnull=False).annotate(
                total_orders=Sum("order_details__quantity"),
                total_amount=Func(
                    Sum("order_details__amount"),
                    function="ROUND",
                    template="%(function)s(%(expressions)s, 2)",
                    output_field=FloatField(),
                ),
                total_users=Count("order_details__order__user", distinct=True),
            )
        ).order_by("id")

        if search_value:
            sales_data = sales_data.filter(Q(name__icontains=search_value))

        if start_date or end_date:
            sales_data = sales_data.filter(**filters)

        if paginate:
            paginator = Paginator(sales_data, 10)  # Paginate results
            page_obj = paginator.get_page(page)
        else:
            page_obj = sales_data

        table_headers = ["Product Name", "Total Orders", "Total Amount", "Unique Users"]
        table_fields = ["name", "total_orders", "total_amount", "total_users"]

        # context = {
        #     "page_obj": page_obj,
        #     "table_headers": [
        #         "Product Name",
        #         "Total Orders",
        #         "Total Amount",
        #         "Unique Users",
        #     ],
        #     "table_fields": [
        #         "name",
        #         "total_orders",
        #         "total_amount",
        #         "total_users",
        #     ],
        #     "start_date": start_date,
        #     "end_date": end_date,
        #     "search_value": search_value,
        # }

        return self.generate_context(
            page_obj,
            table_headers,
            table_fields,
            start_date,
            end_date,
            search_value,
        )

    def user_queryset(self, paginate=True):
        """Fetch user related to user report"""
        # Extract filters from request
        start_date, end_date, search_value, page = self.extract_filters()

        filters = {}
        if start_date:
            filters["date_joined__date__gte"] = start_date
        if end_date:
            filters["date_joined__date__lte"] = end_date

        user_data = (
            User.objects.filter(is_active=True)
            .filter(**filters)
            .annotate(
                total_orders=Coalesce(Count("orders", distinct=True), Value(0)),
                total_products=Coalesce(
                    Sum("orders__order_details__quantity"), Value(0)
                ),
                total_spent=Coalesce(
                    Sum("orders__grand_total", output_field=DecimalField()),
                    Value(0, output_field=DecimalField()),
                ),
                total_used_coupon=Coalesce(Count("orders__coupon"), Value(0)),
                total_discount=Coalesce(
                    Sum(
                        ExpressionWrapper(
                            F("orders__grand_total")
                            * (F("orders__coupon__discount") / 100.0),
                            output_field=IntegerField(),
                        )
                    ),
                    Value(0, output_field=IntegerField()),
                ),
            )
            .prefetch_related("groups")
            .order_by("id")
        )

        if search_value:
            user_data = user_data.filter(
                Q(first_name__icontains=search_value)
                | Q(last_name__icontains=search_value)
            )

        if start_date or end_date:
            user_data = user_data.filter(**filters)

        if paginate:
            paginator = Paginator(user_data, 10)  # Paginate results
            page_obj = paginator.get_page(page)
        else:
            page_obj = user_data  # No pagination, get all results

        table_headers = [
            "First Name",
            "Last Name",
            "Email",
            "Total Orders",
            "Total Coupon Used",
            "Total Discount",
            "Total Spent",
        ]
        table_fields = [
            "first_name",
            "last_name",
            "email",
            "total_orders",
            "total_used_coupon",
            "total_discount",
            "total_spent",
        ]

        # context = {
        #     "page_obj": page_obj,
        #     "table_headers": [
        #         "First Name",
        #         "Last Name",
        #         "Email",
        #         "Total Orders",
        #         "Total Coupon Used",
        #         "Total Discount",
        #         "Total Spent",
        #     ],
        #     "table_fields": [
        #         "first_name",
        #         "last_name",
        #         "email",
        #         "total_orders",
        #         "total_used_coupon",
        #         "total_discount",
        #         "total_spent",
        #     ],
        #     "start_date": start_date,
        #     "end_date": end_date,
        #     "search_value": search_value,
        # }
        return self.generate_context(
            page_obj,
            table_headers,
            table_fields,
            start_date,
            end_date,
            search_value,
        )

    def coupon_queryset(self, paginate=True):
        """Fetch Coupon related to coupon report"""
        # Extract filters from request
        start_date, end_date, search_value, page = self.extract_filters()

        coupon_data = (
            Coupon.objects.filter(is_active=True)
            .annotate(
                count_=Coalesce(
                    Count(
                        "user_orders__id",
                        filter=Q(
                            user_orders__created_at__date__gte=start_date,
                            user_orders__created_at__date__lte=end_date,
                        ),
                    ),
                    Value(0, output_field=IntegerField()),
                ),
                total_sub_total=Coalesce(
                    Sum(
                        "user_orders__order_details__amount",
                        filter=Q(
                            user_orders__created_at__date__gte=start_date,
                            user_orders__created_at__date__lte=end_date,
                        ),
                        output_field=IntegerField(),
                    ),
                    Value(0, output_field=IntegerField()),
                ),
                total_discount=ExpressionWrapper(
                    F("total_sub_total") * (F("discount") / 100.0),
                    output_field=IntegerField(),
                ),
            )
            .order_by("id")
        )

        if search_value:
            coupon_data = coupon_data.filter(
                Q(code__icontains=search_value) | Q(name__icontains=search_value)
            )

        if paginate:
            paginator = Paginator(coupon_data, 10)  # Paginate results
            page_obj = paginator.get_page(page)
        else:
            page_obj = coupon_data  # No pagination, get all results

        context = {
            "page_obj": page_obj,
            "table_headers": [
                "Coupon Name",
                "Coupon Code",
                "Discount(%)",
                "Used Count",
                "Total Discount",
            ],
            "table_fields": [
                "name",
                "code",
                "discount",
                "count_",
                "total_discount",
            ],
            "start_date": start_date,
            "end_date": end_date,
            "search_value": search_value,
        }
        return context

    def get_context_data(self, paginate=True):
        """Return queryset based on the report name."""
        if self.report_name == "sales-report":
            return self.sales_queryset(paginate)
        if self.report_name == "user-report":
            return self.user_queryset(paginate)
        if self.report_name == "coupon-report":
            return self.coupon_queryset(paginate)
        return None

    def get_report_data(self):
        """Get data based on the queryset and format it for reporting."""
        return self.get_context_data(paginate=True)

    def export_report(self, file_type):
        data = self.get_context_data(paginate=False)

        if file_type == "csv":
            return self.export_to_csv(data)
        elif file_type == "pdf":
            return self.export_to_pdf(data)
        else:
            raise ValueError("Invalid file type")

    def export_to_csv(self, data):
        # Create an HttpResponse object with CSV header
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="{self.report_name.replace("-", "_")}.csv"'
        )

        writer = csv.writer(response)

        # If filters or search value exist, include them in the CSV file
        filters = []
        if data.get("start_date"):
            filters.append(f"Start Date: {data['start_date']}")
        if data.get("end_date"):
            filters.append(f"End Date: {data['end_date']}")
        if data.get("search_value"):
            filters.append(f"Search Value: {data['search_value']}")

        if filters:
            writer.writerow([])
            writer.writerow([])
            writer.writerow(["Applied Filters:"] + filters)
            writer.writerow([])
            writer.writerow([])

        # Write table headers
        writer.writerow(data["table_headers"])

        # Write the actual data
        for item in data["page_obj"]:
            writer.writerow([getattr(item, field) for field in data["table_fields"]])

        return response

    def export_to_pdf(self, data):
        """Export data to PDF."""
        context = {
            "data": data["page_obj"],
            "table_headers": data["table_headers"],
            "table_fields": data["table_fields"],
            "start_date": data["start_date"],
            "end_date": data["end_date"],
            "search_value": data["search_value"],
            "report_name": self.report_name.title().replace("-", " "),
        }

        # Render the PDF template with context
        html_string = render_to_string("admin_panel/report_template.html", context)
        pdf = HTML(string=html_string).write_pdf()

        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="{self.report_name.replace("-", "_")}.pdf"'
        )

        return response
