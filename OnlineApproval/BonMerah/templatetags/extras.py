from datetime import datetime
from django import template

register = template.Library()

@register.filter
def days_range(date):
    delta = datetime.now().date() - datetime.date(date) 
    return delta.days