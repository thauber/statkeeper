from django import template
register = template.Library()

def print_filter(var):
    print "Printing variable"
    print var
    print "Done"
    return var
register.filter('print', print_filter)

def fill(incomplete, size):
    return list(incomplete) + [None for i in range(size-len(incomplete))]
register.filter('fill', fill)

def get(var, key):
    if issubclass(type(var),(list,tuple)):
        if issubclass(type(key),(int,long)):
            if key < len(var):
                return var[key]
            else:
                return None
    return var.get(key)
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

def range_filter(var):
    range_list = range(var)
    return range_list
register.filter('range',range_filter)

def for_sides(player_data, all_player_ids):
    player_ids = all_player_ids.split(",")
    return [(player_id, player_data.get(player_id)) for player_id in player_ids]
register.filter('for_sides',for_sides)

def partition(objects, size):
    row_count = len(objects)/size+1
    return [objects[size*i:size*(i+1)] for i in xrange(row_count)]

register.filter('partition', partition)
