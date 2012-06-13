from django.core.management.base import BaseCommand, CommandError
import bracket.tournaments
import importlib

class Command(BaseCommand):
    args = '<tournament script name>'
    help = 'Creates a poll based on a script in /tournaments'

    def handle(self, tournament_name, *args, **options):
        mod = importlib.import_module(
            "%s.%s" % (bracket.tournaments.__name__, tournament_name))
        mod.create_season()
        
