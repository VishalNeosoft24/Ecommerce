from datetime import datetime


def parse_datetimerange(datetimerange):
    # Split the string into start and end parts
    start_str, end_str = datetimerange.split(" - ")

    # Define the date format (adjust if needed)
    date_format = "%m/%d/%Y %I:%M %p"

    # Convert strings to datetime objects
    start_date = datetime.strptime(start_str, date_format)
    end_date = datetime.strptime(end_str, date_format)

    return start_date, end_date
