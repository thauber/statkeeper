# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'MatchPlayer', fields ['match', 'side']
        db.delete_unique('matches_matchplayer', ['match_id', 'side'])

        # Removing unique constraint on 'MatchPlayer', fields ['match', 'player']
        db.delete_unique('matches_matchplayer', ['match_id', 'player_id'])

        # Deleting model 'MatchPlayer'
        db.delete_table('matches_matchplayer')

        # Deleting model 'Match'
        db.delete_table('matches_match')

        # Adding model 'GamePlayer'
        db.create_table('matches_gameplayer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['matches.Game'])),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['matches.Player'])),
            ('side', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('color', self.gf('django.db.models.fields.TextField')(null=True)),
            ('race', self.gf('django.db.models.fields.CharField')(max_length=63)),
        ))
        db.send_create_signal('matches', ['GamePlayer'])

        # Adding unique constraint on 'GamePlayer', fields ['game', 'player']
        db.create_unique('matches_gameplayer', ['game_id', 'player_id'])

        # Adding unique constraint on 'GamePlayer', fields ['game', 'side']
        db.create_unique('matches_gameplayer', ['game_id', 'side'])

        # Adding model 'Game'
        db.create_table('matches_game', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('started', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('finished', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('winner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='won_games', null=True, to=orm['matches.Player'])),
            ('game_map', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['matches.Map'])),
            ('tournament', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('collection', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('game_identifier', self.gf('django.db.models.fields.IntegerField')(max_length=63, null=True)),
            ('set_number', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('matches', ['Game'])

        # Deleting field 'Action.match'
        db.delete_column('matches_action', 'match_id')

        # Adding field 'Action.game'
        db.add_column('matches_action', 'game',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['matches.Game']),
                      keep_default=False)


        # Changing field 'Action.actor'
        db.alter_column('matches_action', 'actor_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['matches.GamePlayer']))
    def backwards(self, orm):
        # Removing unique constraint on 'GamePlayer', fields ['game', 'side']
        db.delete_unique('matches_gameplayer', ['game_id', 'side'])

        # Removing unique constraint on 'GamePlayer', fields ['game', 'player']
        db.delete_unique('matches_gameplayer', ['game_id', 'player_id'])

        # Adding model 'MatchPlayer'
        db.create_table('matches_matchplayer', (
            ('race', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('color', self.gf('django.db.models.fields.TextField')(null=True)),
            ('side', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['matches.Player'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('match', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['matches.Match'])),
        ))
        db.send_create_signal('matches', ['MatchPlayer'])

        # Adding unique constraint on 'MatchPlayer', fields ['match', 'player']
        db.create_unique('matches_matchplayer', ['match_id', 'player_id'])

        # Adding unique constraint on 'MatchPlayer', fields ['match', 'side']
        db.create_unique('matches_matchplayer', ['match_id', 'side'])

        # Adding model 'Match'
        db.create_table('matches_match', (
            ('match_map', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['matches.Map'])),
            ('started', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('tournament', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('collection', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('finished', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('match_identifier', self.gf('django.db.models.fields.IntegerField')(max_length=63, null=True)),
            ('winner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='won_matches', null=True, to=orm['matches.Player'])),
            ('set_number', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('matches', ['Match'])

        # Deleting model 'GamePlayer'
        db.delete_table('matches_gameplayer')

        # Deleting model 'Game'
        db.delete_table('matches_game')


        # User chose to not deal with backwards NULL issues for 'Action.match'
        raise RuntimeError("Cannot reverse this migration. 'Action.match' and its values cannot be restored.")
        # Deleting field 'Action.game'
        db.delete_column('matches_action', 'game_id')


        # Changing field 'Action.actor'
        db.alter_column('matches_action', 'actor_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['matches.MatchPlayer']))
    models = {
        'matches.action': {
            'Meta': {'object_name': 'Action'},
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'actor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'action_actor'", 'null': 'True', 'to': "orm['matches.GamePlayer']"}),
            'changes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'changes_at': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'finished_at': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['matches.Game']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.TextField', [], {}),
            'results': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'started_at': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'matches.game': {
            'Meta': {'object_name': 'Game'},
            'collection': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'finished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'game_identifier': ('django.db.models.fields.IntegerField', [], {'max_length': '63', 'null': 'True'}),
            'game_map': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['matches.Map']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'players': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'games'", 'symmetrical': 'False', 'through': "orm['matches.GamePlayer']", 'to': "orm['matches.Player']"}),
            'set_number': ('django.db.models.fields.IntegerField', [], {}),
            'started': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tournament': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'winner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'won_games'", 'null': 'True', 'to': "orm['matches.Player']"})
        },
        'matches.gameplayer': {
            'Meta': {'unique_together': "(('game', 'player'), ('game', 'side'))", 'object_name': 'GamePlayer'},
            'color': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['matches.Game']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['matches.Player']"}),
            'race': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'side': ('django.db.models.fields.CharField', [], {'max_length': '63'})
        },
        'matches.map': {
            'Meta': {'object_name': 'Map'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'map_file': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'matches.player': {
            'Meta': {'object_name': 'Player'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'official': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['matches']