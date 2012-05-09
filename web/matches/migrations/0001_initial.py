# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Match'
        db.create_table('matches_match', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('winner', self.gf('django.db.models.fields.CharField')(max_length=63, null=True, blank=True)),
            ('match_map', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['matches.Map'], null=True, blank=True)),
        ))
        db.send_create_signal('matches', ['Match'])

        # Adding model 'MatchPlayer'
        db.create_table('matches_matchplayer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('match', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['matches.Match'])),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['matches.Player'])),
            ('side', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('color', self.gf('django.db.models.fields.TextField')(null=True)),
            ('race', self.gf('django.db.models.fields.CharField')(max_length=63)),
        ))
        db.send_create_signal('matches', ['MatchPlayer'])

        # Adding unique constraint on 'MatchPlayer', fields ['match', 'player']
        db.create_unique('matches_matchplayer', ['match_id', 'player_id'])

        # Adding unique constraint on 'MatchPlayer', fields ['match', 'side']
        db.create_unique('matches_matchplayer', ['match_id', 'side'])

        # Adding model 'Action'
        db.create_table('matches_action', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('results', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('reinforcements_at', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('started_at', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('finished_at', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('win_value', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('stage', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('winner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='action_winner', null=True, to=orm['matches.MatchPlayer'])),
            ('actor', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='action_actor', null=True, to=orm['matches.MatchPlayer'])),
            ('match', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['matches.Match'])),
        ))
        db.send_create_signal('matches', ['Action'])

        # Adding model 'Player'
        db.create_table('matches_player', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('official', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('matches', ['Player'])

        # Adding model 'Map'
        db.create_table('matches_map', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('map_file', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('matches', ['Map'])

    def backwards(self, orm):
        # Removing unique constraint on 'MatchPlayer', fields ['match', 'side']
        db.delete_unique('matches_matchplayer', ['match_id', 'side'])

        # Removing unique constraint on 'MatchPlayer', fields ['match', 'player']
        db.delete_unique('matches_matchplayer', ['match_id', 'player_id'])

        # Deleting model 'Match'
        db.delete_table('matches_match')

        # Deleting model 'MatchPlayer'
        db.delete_table('matches_matchplayer')

        # Deleting model 'Action'
        db.delete_table('matches_action')

        # Deleting model 'Player'
        db.delete_table('matches_player')

        # Deleting model 'Map'
        db.delete_table('matches_map')

    models = {
        'matches.action': {
            'Meta': {'object_name': 'Action'},
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'actor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'action_actor'", 'null': 'True', 'to': "orm['matches.MatchPlayer']"}),
            'finished_at': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['matches.Match']"}),
            'reinforcements_at': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'results': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'stage': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'started_at': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'win_value': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'winner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'action_winner'", 'null': 'True', 'to': "orm['matches.MatchPlayer']"})
        },
        'matches.map': {
            'Meta': {'object_name': 'Map'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'map_file': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'matches.match': {
            'Meta': {'object_name': 'Match'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match_map': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['matches.Map']", 'null': 'True', 'blank': 'True'}),
            'players': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['matches.Player']", 'through': "orm['matches.MatchPlayer']", 'symmetrical': 'False'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'winner': ('django.db.models.fields.CharField', [], {'max_length': '63', 'null': 'True', 'blank': 'True'})
        },
        'matches.matchplayer': {
            'Meta': {'unique_together': "(('match', 'player'), ('match', 'side'))", 'object_name': 'MatchPlayer'},
            'color': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['matches.Match']"}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['matches.Player']"}),
            'race': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'side': ('django.db.models.fields.CharField', [], {'max_length': '63'})
        },
        'matches.player': {
            'Meta': {'object_name': 'Player'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'official': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['matches']