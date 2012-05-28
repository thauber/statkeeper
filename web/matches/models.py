from django.db import models
from django.conf import settings
from django.utils import simplejson
from django.template.defaultfilters import slugify

def enumstr(string): return string.replace("_","-")
def enum(*strings):
    slugs = [string.replace("_","-") for string in strings]
    titles = [string.replace("_"," ").title() for string in strings]
    enums = dict(zip(strings, strings))
    enums['_items'] = zip(slugs, strings)
    enums['_choices'] = zip(slugs, titles)
    return type('Enum', (), enums)

Players = enum("left", "right")
ActionTypes = enum("base_invaded", "harassment", "engagement", "unit_creation")
Races = enum("terran", "protoss", "zerg")
TournamentStyle = enum("GSL",)

ActionInfo = {
    ActionTypes.base_invaded: {'symmetric':False, 'expandable':True},
    ActionTypes.harassment: {'symmetric':True, 'expandable':True},
    ActionTypes.engagement: {'symmetric':False, 'expandable':True},
    ActionTypes.unit_creation: {'symmetric':False, 'expandable':False},
}

class Game(models.Model):
    started = models.BooleanField()
    finished = models.BooleanField()
    winner = models.ForeignKey(
        "Player", null=True, related_name="won_games")
    game_map = models.ForeignKey('Map')
    game_number = models.IntegerField()
    match = models.ForeignKey("Match", related_name="games")

    class Meta:
        unique_together = (("match","game_number"),)

    @property
    def players(self):
        return self.match.players

    def to_dict(self):
        return dict(
            winner          = self.winner_id,
            game_map        = self.game_map.to_dict(),
            started         = self.started,
            finished        = self.finished,
            id              = self.id,
        )

class Tournament(models.Model):
    name = models.CharField(max_length=63, unique=True)
    slug = models.CharField(max_length=63)
    style = models.CharField(
        max_length=63,
        choices=TournamentStyle._choices
    )
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super(Tournament, self).save(*args, **kwargs)

class Collection(models.Model):
    tournament = models.ForeignKey("Tournament")
    name = models.CharField(max_length=63)
    slug = models.CharField(max_length=63)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super(Collection, self).save(*args, **kwargs)

    class Meta:
        unique_together = (("tournament", "slug"),)

class Match(models.Model):
    collection = models.ForeignKey("Collection")
    players = models.ManyToManyField("Player", through="MatchPlayer")
    match_identifier = models.IntegerField(null=True)
    slug = models.CharField(max_length=255)

    class Meta:
        unique_together = (('collection', 'slug'),)

    def to_dict(self):
        left_player = self.matchplayer_set.filter(side="left")[0]
        right_player = self.matchplayer_set.filter(side="right")[0]
        left_wins = 0
        right_wins = 0
        for game in self.games.all():
            if game.winner_id == left_player.player.id:
                left_wins += 1
            if game.winner_id == right_player.player.id:
                right_wins += 1
        data = dict (
            wins = dict (
                left = left_wins,
                right = right_wins,
            ),
            players = dict (
                left = left_player.to_dict(),
                right = right_player.to_dict(),
            ),
            tournament = self.collection.tournament.name,
            collection = self.collection.name,
        )
        return data;

    @classmethod
    def create_slug(self, players):
        slug = ""
        for i, player in enumerate(players):
            if i:
                slug += "-vs-"
            slug += player.name.lower()
        return slug
        

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
    game = models.ForeignKey('Game', related_name="actions")


    def _result_list(self):
        return simplejson.loads(self.results)
    def _set_result_list(self, result_list):
        self.results = simplejson.dumps(result_list)
    result_list = property(_result_list, _set_result_list)

    def _position_dict(self):
        if len(self.position) == 0:
            return None
        return simplejson.loads(self.position)
    def _set_position_dict(self, position_dict):
        self.position = simplejson.dumps(position_dict)
    position_dict = property(_position_dict, _set_position_dict)

    def to_dict(self):
        data = dict(
            acting_side     = self.actor and self.actor.side,
            action_type     = self.action_type,
            results         = self.result_list,
            position        = self.position_dict, 
            changes_at      = self.changes_at,
            changes         = self.changes,
            started_at      = self.started_at,
            finished_at     = self.finished_at,
            id              = self.id,
        )
        if self.action_type == "unit_creation":
            macro_result = self.get_result('macro')
            for key, value in macro_result.items():
                if key != 'type':
                    data['force'] = value
                    break
        win = self.get_result('win')
        if win:
            data['winning_side'] = win['winner']
            data['win_value'] = win['win_value']
        data.update(ActionInfo[self.action_type])

        return data

    def get_result(self, result_type):
        results = self.get_results(result_type)
        if len(results):
            return results[0]
        return None

    def get_results(self, result_type):
        typed_results = [];
        for result in self.result_list:
            if result.get("type") == result_type:
                typed_results.append(result)
        return typed_results

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
