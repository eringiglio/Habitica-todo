# -*- coding: utf-8 -*-
""" Datetime functions
"""

# Ensure backwards compatibility with Python 2
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals)
from builtins import *

from datetime import datetime
import iso8601
import pytz
from tzlocal import get_localzone

def parse_date_utc(date, milliseconds=True):
    """Parses dates from ISO8601 or Epoch formats to a standard datetime object.

    This is particularly useful since Habitica returns dates in two
    formats::

        - iso8601 encoded strings
        - Long integer Epoch times

    Args:
        date (str): A date string in either iso8601 or Epoch format.
        milliseconds (bool): If True, then epoch times are treated as
            millisecond values, otherwise they are evaluated as seconds.

    Returns:
        datetime: The parsed date time in UTC.
    """

    parsed_date = None
    try:
        parsed_date = iso8601.parse_date(date)
    except iso8601.ParseError:
        value = int(date)
        # utcfromtimestamp expects values in seconds
        if milliseconds:
            value /= 1000
        parsed_date = datetime.utcfromtimestamp(value)

    return parsed_date.replace(tzinfo=pytz.utc)

def parse_date_local(date, milliseconds=True):
    """Parses dates from ISO8601 or Epoch formats to a standard datetime object
    in the current local timezone.

    **Note that this function should not be used in time calculations.**
    **It is primarily intended for displaying dates and times to the user.**

    Args:
        date (str): A date string in either iso8601 or Epoch format.
        milliseconds (bool): If True, then epoch times are treated as
            millisecond values, otherwise they are evaluated as seconds.

    Returns:
        datetime: The parsed date time in local time.
    """
    return parse_date_utc(date, milliseconds).astimezone(get_localzone())
