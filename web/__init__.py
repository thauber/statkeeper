import sys 
import os
import traceback
 
from django.core.signals import got_request_exception
 
def print_exception(f):
    f.write(''.join(traceback.format_exception(*sys.exc_info())) + '\n\n')
 
def exception_printer(sender, **kwargs):
    f = sys.stdout
    print_exception(f)

got_request_exception.connect(exception_printer)

