from django.db import models

def enumstr(string):
    return string.replace("_","-")

def enum(*strings):
    slugs = [string.replace("_","-") for string in strings]
    titles = [string.replace("_"," ").title() for string in strings]
    enums = dict(zip(strings, slugs))
    enums['_items'] = zip(strings, slugs)
    enums['_choices'] = zip(titles, slugs)
    return type('Enum', (), enums)

MatchStates = enum('unpublished', 'published', 'started', 'ended')
ActionStages = enum('inprogress', 'reinforcing', 'queued', 'ongoing',
                    'won', 'finished', 'hidden')
Players = enum("left", "right")
ActionTypes = enum("base_invasion", "harrassment", "engagement")
Races = enum("terran", "protoss", "zerg")

class Match(models.Model):
    state = models.CharField(max_length=63, choices=MatchStates._choices)
    players = models.ManyToManyField("Player", through="MatchPlayer")
    winner = models.CharField(
        max_length=63, choices=Players._choices, null=True, blank=True)
    match_map = models.ForeignKey('Map', null=True, blank=True)

    def to_dict(self):
        return dict(
            state           = self.state,
            winner          = self.winner,
            match_map       = self.match_map,
            id              = self.id,
        )

class MatchPlayer(models.Model):
    match = models.ForeignKey('Match')
    player = models.ForeignKey('Player')
    side = models.CharField(max_length=63, choices=Players._choices)
    color = models.TextField(null=True)
    race = models.CharField(max_length=63, choices=Races._choices)
        
    class Meta:
        unique_together = (("match", "player"),("match", "side"))

class Action(models.Model):
    action_type = models.CharField(max_length=63, choices=ActionTypes._choices)
    results = models.TextField(null=True, blank=True)
    reinforcements_at = models.TextField(null=True, blank=True)
    started_at = models.FloatField(null=True, blank=True)
    finished_at = models.FloatField(null=True, blank=True)
    win_value = models.IntegerField(null=True, blank=True)
    stage = models.CharField(max_length=63, choices=ActionStages._choices)
    winner = models.ForeignKey('MatchPlayer',
        null=True, blank=True, related_name="action_winner")
    actor = models.ForeignKey('MatchPlayer',
        null=True, blank=True, related_name="action_actor")
    match = models.ForeignKey('Match')

    def to_dict(self):
        return dict(
            action_type         = self.action_type,
            results             = self.results,
            reinforcements_at   = self.reinforcements_at,
            started_at          = self.started_at,
            finished_at         = self.finished_at,
            winner              = self.winner,
            win_value           = self.win_value,
            stage               = self.stage,
            id                  = self.id,
        )

class Player(models.Model):
    name = models.TextField()
    official = models.BooleanField(default=False)

class Map(models.Model):
    map_file = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
