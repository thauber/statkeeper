from django import template
register = template.Library()

def partition(objects, size):
    row_count = len(objects)/size+1
    return [objects[size*i:size*(i+1)] for i in xrange(row_count)]

register.filter('partition', partition)
