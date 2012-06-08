# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Tournament.start_date'
        db.add_column('matches_tournament', 'start_date',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 3, 12, 0, 0)),
                      keep_default=False)

        # Adding field 'Season.start_date'
        db.add_column('matches_season', 'start_date',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 3, 29, 0, 0)),
                      keep_default=False)

        # Adding field 'Match.start_date'
        db.add_column('matches_match', 'start_date',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 3, 29, 0, 0)),
                      keep_default=False)

        # Adding field 'Collection.start_date'
        db.add_column('matches_collection', 'start_date',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 3, 29, 0, 0)),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'Tournament.start_date'
        db.delete_column('matches_tournament', 'start_date')

        # Deleting field 'Season.start_date'
        db.delete_column('matches_season', 'start_date')

        # Deleting field 'Match.start_date'
        db.delete_column('matches_match', 'start_date')

        # Deleting field 'Collection.start_date'
        db.delete_column('matches_collection', 'start_date')

    models = {
        'matches.action': {
            'Meta': {'object_name': 'Action'},
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'actor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'action_actor'", 'null': 'True', 'to': "orm['matches.MatchPlayer']"}),
            'changes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'changes_at': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'finished_at': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'actions'", 'to': "orm['matches.Game']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.TextField', [], {}),
            'results': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'started_at': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'matches.bracketpath': {
            'Meta': {'object_name': 'BracketPath'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'next_match': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'next_paths'", 'to': "orm['matches.Match']"}),
            'prev_match': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'prve_paths'", 'to': "orm['matches.Match']"}),
            'qualifier': ('django.db.models.fields.TextField', [], {'max_length': '63'})
        },
        'matches.collection': {
            'Meta': {'unique_together': "(('tournament', 'slug'),)", 'object_name': 'Collection'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {}),
            'tournament': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['matches.Tournament']"})
        },
        'matches.game': {
            'Meta': {'unique_together': "(('match', 'game_number'),)", 'object_name': 'Game'},
            'finished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'game_map': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['matches.Map']"}),
            'game_number': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'games'", 'to': "orm['matches.Match']"}),
            'started': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'winner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'won_games'", 'null': 'True', 'to': "orm['matches.Player']"})
        },
        'matches.league': {
            'Meta': {'object_name': 'League'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '63'})
        },
        'matches.map': {
            'Meta': {'object_name': 'Map'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'map_file': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'matches.match': {
            'Meta': {'unique_together': "(('collection', 'slug'),)", 'object_name': 'Match'},
            'best_of': ('django.db.models.fields.IntegerField', [], {}),
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['matches.Collection']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match_identifier': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'players': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['matches.Player']", 'through': "orm['matches.MatchPlayer']", 'symmetrical': 'False'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {})
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
        },
        'matches.season': {
            'Meta': {'object_name': 'Season'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'league': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['matches.League']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {})
        },
        'matches.tournament': {
            'Meta': {'object_name': 'Tournament'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '63'}),
            'season': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['matches.League']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {}),
            'style': ('django.db.models.fields.CharField', [], {'max_length': '63'})
        }
    }

    complete_apps = ['matches']