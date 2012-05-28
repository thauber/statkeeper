# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Game'
        db.create_table('matches_game', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('started', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('finished', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('winner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='won_games', null=True, to=orm['matches.Player'])),
            ('game_map', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['matches.Map'])),
            ('game_number', self.gf('django.db.models.fields.IntegerField')()),
            ('match', self.gf('django.db.models.fields.related.ForeignKey')(related_name='games', to=orm['matches.Match'])),
        ))
        db.send_create_signal('matches', ['Game'])

        # Adding unique constraint on 'Game', fields ['match', 'game_number']
        db.create_unique('matches_game', ['match_id', 'game_number'])

        # Adding model 'Tournament'
        db.create_table('matches_tournament', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=63)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('style', self.gf('django.db.models.fields.CharField')(max_length=63)),
        ))
        db.send_create_signal('matches', ['Tournament'])

        # Adding model 'Collection'
        db.create_table('matches_collection', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tournament', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['matches.Tournament'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=63)),
        ))
        db.send_create_signal('matches', ['Collection'])

        # Adding unique constraint on 'Collection', fields ['tournament', 'slug']
        db.create_unique('matches_collection', ['tournament_id', 'slug'])

        # Adding model 'Match'
        db.create_table('matches_match', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['matches.Collection'])),
            ('match_identifier', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('matches', ['Match'])

        # Adding unique constraint on 'Match', fields ['collection', 'slug']
        db.create_unique('matches_match', ['collection_id', 'slug'])

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
            ('position', self.gf('django.db.models.fields.TextField')()),
            ('changes_at', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('changes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('started_at', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('finished_at', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('actor', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='action_actor', null=True, to=orm['matches.MatchPlayer'])),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(related_name='actions', to=orm['matches.Game'])),
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
            ('slug', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('matches', ['Map'])

    def backwards(self, orm):
        # Removing unique constraint on 'MatchPlayer', fields ['match', 'side']
        db.delete_unique('matches_matchplayer', ['match_id', 'side'])

        # Removing unique constraint on 'MatchPlayer', fields ['match', 'player']
        db.delete_unique('matches_matchplayer', ['match_id', 'player_id'])

        # Removing unique constraint on 'Match', fields ['collection', 'slug']
        db.delete_unique('matches_match', ['collection_id', 'slug'])

        # Removing unique constraint on 'Collection', fields ['tournament', 'slug']
        db.delete_unique('matches_collection', ['tournament_id', 'slug'])

        # Removing unique constraint on 'Game', fields ['match', 'game_number']
        db.delete_unique('matches_game', ['match_id', 'game_number'])

        # Deleting model 'Game'
        db.delete_table('matches_game')

        # Deleting model 'Tournament'
        db.delete_table('matches_tournament')

        # Deleting model 'Collection'
        db.delete_table('matches_collection')

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
            'changes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'changes_at': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'finished_at': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'actions'", 'to': "orm['matches.Game']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.TextField', [], {}),
            'results': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'started_at': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'matches.collection': {
            'Meta': {'unique_together': "(('tournament', 'slug'),)", 'object_name': 'Collection'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
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
        'matches.map': {
            'Meta': {'object_name': 'Map'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'map_file': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'matches.match': {
            'Meta': {'unique_together': "(('collection', 'slug'),)", 'object_name': 'Match'},
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['matches.Collection']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match_identifier': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'players': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['matches.Player']", 'through': "orm['matches.MatchPlayer']", 'symmetrical': 'False'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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
        'matches.tournament': {
            'Meta': {'object_name': 'Tournament'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '63'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'style': ('django.db.models.fields.CharField', [], {'max_length': '63'})
        }
    }

    complete_apps = ['matches']