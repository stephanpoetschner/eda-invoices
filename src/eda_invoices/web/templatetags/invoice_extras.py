import datetime

from dateutil import relativedelta
from django import template

register = template.Library()


@register.filter
def end_of_month(date: datetime.date):
    """Removes all values of arg from the given string"""
    end_of_month = (
        date + relativedelta.relativedelta(months=1) - datetime.timedelta(days=1)
    )
    return end_of_month
