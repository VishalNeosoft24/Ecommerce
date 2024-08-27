from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Q


def parse_datetimerange(datetimerange):
    # Split the string into start and end parts
    start_str, end_str = datetimerange.split(" - ")

    # Define the date format (adjust if needed)
    date_format = "%m/%d/%Y %I:%M %p"

    # Convert strings to datetime objects
    start_date = datetime.strptime(start_str, date_format)
    end_date = datetime.strptime(end_str, date_format)

    return start_date, end_date


def paginated_response(request, data):
    """
    request for vars like Draw, start, length, search
    data for [{}] list of dicts
    """
    draw = int(request.GET.get("draw", 1))
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))

    paginator = Paginator(data, length)
    page_number = (start // length) + 1
    page = paginator.get_page(page_number)
    data_paginated = list(page.object_list)

    response = {
        "start": start,
        "draw": draw,
        "recordsTotal": len(data),
        "recordsFiltered": paginator.count,
        "data": data_paginated,
    }

    return response


def format_datetime(datetime_value, format_string="%Y-%m-%d %H:%M"):
    """
    Formats a datetime value into a human-readable string.

    :param datetime_value: A datetime object to be formatted.
    :param format_string: A string specifying the format. Default is '%Y-%m-%d %H:%M:%S'.
    :return: A formatted date string.
    """
    if datetime_value:
        return datetime_value.strftime(format_string)
    return None


def build_search_query(request, search_fields):
    search_val = request.GET.get("search[value]", "").strip()
    query = Q()
    if search_val:
        queries = Q()
        for field in search_fields:
            queries |= Q(**{f"{field}__icontains": search_val})
        query = queries
    return query
