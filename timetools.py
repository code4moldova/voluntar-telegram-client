"""Some tools for converting between different timezones. Internally all timestamps are UTC,
but we adapt them to the timezone of the user before displaying. We assume that:
- all the users are in a single timezone, specified in c.TIMEZONE
- the timezone of the bot is not necessarily the same as the timezone of the users
- all the time-related data we receive from the backend is also in UTC
"""

from datetime import datetime

import pytz

import constants as c

local_timezone = pytz.timezone(c.TIMEZONE)
time_difference = local_timezone.utcoffset(datetime.utcnow())


def user_now():
    """Return the current time, relative to the users' timezone"""
    utcnow = datetime.utcnow()
    usernow = utcnow + time_difference
    return usernow


def utc_to_user(dt):
    """Convert a naive UTC datetime to a naive datetime in the user's timezone"""
    return dt + time_difference


def user_to_utc(dt):
    """Convert a naive UTC datetime to a naive datetime in the user's timezone"""
    return dt - time_difference


def utc_short_to_user_short(short_time):
    """Transform a short '%H:%M' time notation from UTC to the user's timezone
    :params short_time: str, timestamp in %H:%M format
    :returns: str, timestamp in the same format, but adapted to the user's timezone"""
    raw = datetime.strptime(short_time, "%H:%M")
    localized = raw + time_difference
    return localized.strftime("%H:%M")


if __name__ == "__main__":
    print("UTC: %s" % datetime.utcnow())
    print("Delta UTC/user: %s" % time_difference)
    print("User now: %s" % user_now())
    print(utc_short_to_user_short("12:35"))
