from django import forms
from django.contrib.admin.widgets import AdminDateWidget 
from matches.models import Match, MatchPlayer
import datetime

class MatchPlayerForm(forms.ModelForm):
    class Meta:
        model = MatchPlayer
        fields = ('player', 'race')


class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ('match_map', 'tournament', 'set_number', 'match_identifier')
    tournament = forms.ChoiceField(
        label="Season", choices=[("GSL Season 2 Code S", "GSL Season 2 Code S")])
    ro = forms.ChoiceField(label="Round of", choices=[
        ("32","32"),
        ("16","16"),
        ("8","8"),
        ("4","4"),
        ("Championship","Championship"),
    ])
    group = forms.ChoiceField(label="Group", choices=[
        ("A","A"),
        ("B","B"),
        ("C","C"),
        ("D","D"),
        ("E","E"),
        ("F","F"),
        ("G","G"),
        ("H","H"),
    ])
    match_identifier = forms.IntegerField(label="Match Number")
    set_number = forms.IntegerField(label="Set Number")

    def get_collection(self):
        return "Round of %s: Group %s" % (
            self.cleaned_data['ro'], self.cleaned_data['group'])
