from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Q


def parse_datetimerange(datetimerange):
    """
    Parses a date-time range string into two separate datetime objects.

    The input string should be in the format "MM/DD/YYYY HH:MM AM/PM - MM/DD/YYYY HH:MM AM/PM".
    The function splits this string into start and end date-time strings, converts them into
    datetime objects, and returns these objects.

    Args:
        datetimerange (str): A string representing a date-time range in the format
        "MM/DD/YYYY HH:MM AM/PM - MM/DD/YYYY HH:MM AM/PM".

    Returns:
        tuple: A tuple containing two datetime objects (start_date, end_date).
    """

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
    """
    Builds a search query based on the search value provided in the request.

    The function constructs a Django Q object that can be used to filter querysets based on
    the search value. The search value is compared against the specified search fields using
    an `icontains` lookup.

    Args:
        request (HttpRequest): The HTTP request object containing the search value.
        search_fields (list): A list of field names to be included in the search query.

    Returns:
        Q: A Django Q object representing the search query.
    """

    search_val = request.GET.get("search[value]", "").strip()
    query = Q()
    if search_val:
        queries = Q()
        for field in search_fields:
            queries |= Q(**{f"{field}__icontains": search_val})
        query = queries
    return query
