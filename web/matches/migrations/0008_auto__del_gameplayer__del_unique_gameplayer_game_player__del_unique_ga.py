# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'GamePlayer', fields ['game', 'side']
        db.delete_unique('matches_gameplayer', ['game_id', 'side'])

        # Removing unique constraint on 'GamePlayer', fields ['game', 'player']
        db.delete_unique('matches_gameplayer', ['game_id', 'player_id'])

        # Deleting model 'GamePlayer'
        db.delete_table('matches_gameplayer')

        # Adding model 'Tournament'
        db.create_table('matches_tournament', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=63)),
        ))
        db.send_create_signal('matches', ['Tournament'])

        # Adding model 'Match'
        db.create_table('matches_match', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tournament', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['matches.Tournament'])),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['matches.Collection'])),
            ('match_identifier', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('matches', ['Match'])

        # Adding unique constraint on 'Match', fields ['tournament', 'collection', 'slug']
        db.create_unique('matches_match', ['tournament_id', 'collection_id', 'slug'])

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

        # Adding model 'Collection'
        db.create_table('matches_collection', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tournament', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['matches.Tournament'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=63)),
        ))
        db.send_create_signal('matches', ['Collection'])

        # Adding unique constraint on 'Collection', fields ['tournament', 'name']
        db.create_unique('matches_collection', ['tournament_id', 'name'])

        # Deleting field 'Game.tournament'
        db.delete_column('matches_game', 'tournament')

        # Deleting field 'Game.collection'
        db.delete_column('matches_game', 'collection')

        # Deleting field 'Game.set_number'
        db.delete_column('matches_game', 'set_number')

        # Deleting field 'Game.game_identifier'
        db.delete_column('matches_game', 'game_identifier')

        # Adding field 'Game.game_number'
        db.add_column('matches_game', 'game_number',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)

        # Adding field 'Game.match'
        db.add_column('matches_game', 'match',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['matches.Match']),
                      keep_default=False)


        # Changing field 'Action.actor'
        db.alter_column('matches_action', 'actor_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['matches.MatchPlayer']))
    def backwards(self, orm):
        # Removing unique constraint on 'Collection', fields ['tournament', 'name']
        db.delete_unique('matches_collection', ['tournament_id', 'name'])

        # Removing unique constraint on 'MatchPlayer', fields ['match', 'side']
        db.delete_unique('matches_matchplayer', ['match_id', 'side'])

        # Removing unique constraint on 'MatchPlayer', fields ['match', 'player']
        db.delete_unique('matches_matchplayer', ['match_id', 'player_id'])

        # Removing unique constraint on 'Match', fields ['tournament', 'collection', 'slug']
        db.delete_unique('matches_match', ['tournament_id', 'collection_id', 'slug'])

        # Adding model 'GamePlayer'
        db.create_table('matches_gameplayer', (
            ('race', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('color', self.gf('django.db.models.fields.TextField')(null=True)),
            ('side', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['matches.Player'])),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['matches.Game'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('matches', ['GamePlayer'])

        # Adding unique constraint on 'GamePlayer', fields ['game', 'player']
        db.create_unique('matches_gameplayer', ['game_id', 'player_id'])

        # Adding unique constraint on 'GamePlayer', fields ['game', 'side']
        db.create_unique('matches_gameplayer', ['game_id', 'side'])

        # Deleting model 'Tournament'
        db.delete_table('matches_tournament')

        # Deleting model 'Match'
        db.delete_table('matches_match')

        # Deleting model 'MatchPlayer'
        db.delete_table('matches_matchplayer')

        # Deleting model 'Collection'
        db.delete_table('matches_collection')


        # User chose to not deal with backwards NULL issues for 'Game.tournament'
        raise RuntimeError("Cannot reverse this migration. 'Game.tournament' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Game.collection'
        raise RuntimeError("Cannot reverse this migration. 'Game.collection' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Game.set_number'
        raise RuntimeError("Cannot reverse this migration. 'Game.set_number' and its values cannot be restored.")
        # Adding field 'Game.game_identifier'
        db.add_column('matches_game', 'game_identifier',
                      self.gf('django.db.models.fields.IntegerField')(max_length=63, null=True),
                      keep_default=False)

        # Deleting field 'Game.game_number'
        db.delete_column('matches_game', 'game_number')

        # Deleting field 'Game.match'
        db.delete_column('matches_game', 'match_id')


        # Changing field 'Action.actor'
        db.alter_column('matches_action', 'actor_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['matches.GamePlayer']))
    models = {
        'matches.action': {
            'Meta': {'object_name': 'Action'},
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'actor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'action_actor'", 'null': 'True', 'to': "orm['matches.MatchPlayer']"}),
            'changes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'changes_at': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'finished_at': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['matches.Game']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.TextField', [], {}),
            'results': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'started_at': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'matches.collection': {
            'Meta': {'unique_together': "(('tournament', 'name'),)", 'object_name': 'Collection'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'tournament': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['matches.Tournament']"})
        },
        'matches.game': {
            'Meta': {'object_name': 'Game'},
            'finished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'game_map': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['matches.Map']"}),
            'game_number': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['matches.Match']"}),
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
            'Meta': {'unique_together': "(('tournament', 'collection', 'slug'),)", 'object_name': 'Match'},
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['matches.Collection']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match_identifier': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'players': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['matches.Player']", 'through': "orm['matches.MatchPlayer']", 'symmetrical': 'False'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tournament': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['matches.Tournament']"})
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
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '63'})
        }
    }

    complete_apps = ['matches']