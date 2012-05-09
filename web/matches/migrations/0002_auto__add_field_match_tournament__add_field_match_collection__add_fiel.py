# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Match.tournament'
        db.add_column('matches_match', 'tournament',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=63),
                      keep_default=False)

        # Adding field 'Match.collection'
        db.add_column('matches_match', 'collection',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=63),
                      keep_default=False)

        # Adding field 'Match.match_identifier'
        db.add_column('matches_match', 'match_identifier',
                      self.gf('django.db.models.fields.IntegerField')(max_length=63, null=True),
                      keep_default=False)

        # Adding field 'Match.set_number'
        db.add_column('matches_match', 'set_number',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


        # Changing field 'Match.match_map'
        db.alter_column('matches_match', 'match_map_id', self.gf('django.db.models.fields.related.ForeignKey')(default='', to=orm['matches.Map']))
    def backwards(self, orm):
        # Deleting field 'Match.tournament'
        db.delete_column('matches_match', 'tournament')

        # Deleting field 'Match.collection'
        db.delete_column('matches_match', 'collection')

        # Deleting field 'Match.match_identifier'
        db.delete_column('matches_match', 'match_identifier')

        # Deleting field 'Match.set_number'
        db.delete_column('matches_match', 'set_number')


        # Changing field 'Match.match_map'
        db.alter_column('matches_match', 'match_map_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['matches.Map'], null=True))
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
            'collection': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match_identifier': ('django.db.models.fields.IntegerField', [], {'max_length': '63', 'null': 'True'}),
            'match_map': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['matches.Map']"}),
            'players': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['matches.Player']", 'through': "orm['matches.MatchPlayer']", 'symmetrical': 'False'}),
            'set_number': ('django.db.models.fields.IntegerField', [], {}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'tournament': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
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