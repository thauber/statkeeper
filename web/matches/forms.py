from django import forms
from django.contrib.admin.widgets import AdminDateWidget 
from matches.models import Game, MatchPlayer, Match
import datetime

class MatchPlayerForm(forms.ModelForm):
    class Meta:
        model = MatchPlayer
        fields = ('player', 'race')

class MatchForm(forms.Form):
    collection = forms.CharField(max_length=63,)# widget=forms.HiddenInput)
    match_identifier = forms.IntegerField(label="Match Number")
    best_of = forms.IntegerField()

class GameForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(GameForm, self).__init__(*args, **kwargs)
        self.fields['game_map'].label = "Map"
        self.fields['game_number'].label = "Game Number"
    class Meta:
        model = Game
        fields = ('game_map', 'game_number')

class MapForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ('game_map',)
