from django import template
register = template.Library()

def get(var, key):
    return var[key]

register.filter('get', get)

def clock(var):
    minutes = int(var/60)
    minute_zero = ""
    if minutes < 10:
        minute_zero = "0"
    seconds = int(var%60)
    second_zero = ""
    if seconds < 10:
        second_zero = "0"
    return "%s%d:%s%d" % (minute_zero, minutes, second_zero, seconds)
register.filter('clock',clock)

def iconify(var):
    return var.replace(" ", "_").lower()
register.filter('iconify',iconify)

