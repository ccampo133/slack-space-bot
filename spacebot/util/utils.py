import datetime


def field(name, value, short=True):
    return {"title": name, "value": value, "short": short}


def validate_date(date_string):
    try:
        datetime.datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")

