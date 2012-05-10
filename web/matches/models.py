from django.db import models
from django.conf import settings

def enumstr(string): return string.replace("_","-")
def enum(*strings):
    slugs = [string.replace("_","-") for string in strings]
    titles = [string.replace("_"," ").title() for string in strings]
    enums = dict(zip(strings, slugs))
    enums['_items'] = zip(slugs, strings)
    enums['_choices'] = zip(slugs, titles)
    return type('Enum', (), enums)

MatchStates = enum('unpublished', 'published', 'started', 'ended')
ActionStages = enum('inprogress', 'reinforcing', 'queued', 'ongoing',
                    'won', 'finished', 'hidden')
Players = enum("left", "right")
ActionTypes = enum("base_invasion", "harrassment", "engagement")
Races = enum("terran", "protoss", "zerg")

class Match(models.Model):
    started = models.BooleanField()
    ended = models.BooleanField()
    players = models.ManyToManyField(
        "Player", through="MatchPlayer", related_name="matches")
    winner = models.ForeignKey(
        "Player", null=True, related_name="won_matches")
    match_map = models.ForeignKey('Map')
    tournament = models.CharField(max_length=63)
    collection = models.CharField(max_length=63)
    match_identifier = models.IntegerField(max_length=63, null=True)
    set_number = models.IntegerField()

    def to_dict(self):
        return dict(
            state           = self.state,
            winner          = self.winner,
            match_map       = self.match_map.to_dict(),
            id              = self.id,
        )

class MatchPlayer(models.Model):
    match = models.ForeignKey('Match')
    player = models.ForeignKey('Player')
    side = models.CharField(max_length=63, choices=Players._choices)
    color = models.TextField(null=True)
    race = models.CharField(max_length=63, choices=Races._choices)

    def to_dict(self):
        return dict (
            name = self.player.name,
            race = self.race,
            player_id = self.player_id,
            side = self.side,
        )

    class Meta:
        unique_together = (("match", "player"),("match", "side"))

class Action(models.Model):
    action_type = models.CharField(max_length=63, choices=ActionTypes._choices)
    results = models.TextField(null=True, blank=True)
    position = models.TextField()
    changes_at = models.TextField(null=True, blank=True)
    changes = models.TextField(null=True, blank=True)
    started_at = models.FloatField(null=True, blank=True)
    finished_at = models.FloatField(null=True, blank=True)
    actor = models.ForeignKey('MatchPlayer',
        null=True, blank=True, related_name="action_actor")
    match = models.ForeignKey('Match')

    def to_dict(self):
        return dict(
            action_type         = self.action_type,
            results             = self.results,
            changes_at          = self.changes_at,
            changes             = self.changes,
            started_at          = self.started_at,
            finished_at         = self.finished_at,
            id                  = self.id,
        )

class Player(models.Model):
    name = models.TextField()
    official = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

class Map(models.Model):
    map_file = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)

    def to_dict(self):
        return dict(
            url = "%s%s" % (settings.MEDIA_URL, self.map_file),
            slug = self.slug,
            name = self.name
        )

    def __unicode__(self):
        return self.name
