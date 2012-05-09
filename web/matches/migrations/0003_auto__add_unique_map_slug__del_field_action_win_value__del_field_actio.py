# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'Map', fields ['slug']
        db.create_unique('matches_map', ['slug'])

        # Deleting field 'Action.win_value'
        db.delete_column('matches_action', 'win_value')

        # Deleting field 'Action.reinforcements_at'
        db.delete_column('matches_action', 'reinforcements_at')

        # Deleting field 'Action.stage'
        db.delete_column('matches_action', 'stage')

        # Deleting field 'Action.winner'
        db.delete_column('matches_action', 'winner_id')

        # Adding field 'Action.position'
        db.add_column('matches_action', 'position',
                      self.gf('django.db.models.fields.TextField')(default='{x:0, y:0}'),
                      keep_default=False)

        # Adding field 'Action.changes_at'
        db.add_column('matches_action', 'changes_at',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Action.changes'
        db.add_column('matches_action', 'changes',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

    def backwards(self, orm):
        # Removing unique constraint on 'Map', fields ['slug']
        db.delete_unique('matches_map', ['slug'])

        # Adding field 'Action.win_value'
        db.add_column('matches_action', 'win_value',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Action.reinforcements_at'
        db.add_column('matches_action', 'reinforcements_at',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Action.stage'
        raise RuntimeError("Cannot reverse this migration. 'Action.stage' and its values cannot be restored.")
        # Adding field 'Action.winner'
        db.add_column('matches_action', 'winner',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='action_winner', null=True, to=orm['matches.MatchPlayer'], blank=True),
                      keep_default=False)

        # Deleting field 'Action.position'
        db.delete_column('matches_action', 'position')

        # Deleting field 'Action.changes_at'
        db.delete_column('matches_action', 'changes_at')

        # Deleting field 'Action.changes'
        db.delete_column('matches_action', 'changes')

    models = {
        'matches.action': {
            'Meta': {'object_name': 'Action'},
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'actor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'action_actor'", 'null': 'True', 'to': "orm['matches.MatchPlayer']"}),
            'changes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'changes_at': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'finished_at': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['matches.Match']"}),
            'position': ('django.db.models.fields.TextField', [], {}),
            'results': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'started_at': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'matches.map': {
            'Meta': {'object_name': 'Map'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'map_file': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
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