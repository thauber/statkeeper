from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
from django.http import HttpResponse, QueryDict, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.urlresolvers import reverse
import models
import utils

from django_ext.http import JSONResponse
from django.template.response import TemplateResponse

from matches.forms import GameForm, MatchPlayerForm, MapForm, MatchForm

def match_detail(request, tournament_slug, collection_slug, match_slug):
    tournament = models.Tournament.objects.get(slug = tournament_slug)
    collection = models.Collection.objects.get(
        slug = collection_slug,
        tournament=tournament
    )
    match = models.Match.objects.get(
        collection=collection,
        slug=match_slug
    )
    match_dict = match.to_dict()
    games = match.games.all().order_by('game_number')
    actions = []
    for game in games:
        actions += game.actions.all()
    
    harassment_ratios = {}
    base_invasion_ratios = {}
    engagements_won = {}
    for side in ['left', 'right']:
        harassment_ratios[side] = utils.get_attempted_successful(
            side,
            models.ActionTypes.harassment,
            actions
        )
        base_invasion_ratios[side] = utils.get_attempted_successful(
            side,
            models.ActionTypes.base_invaded,
            actions
        )
        _, engagements_won[side] = utils.get_attempted_successful(
            side,
            models.ActionTypes.engagement,
            actions
        )
    game_dicts = []
    for game in games:
        game_dict = game.to_dict()
        game_dict['actions'] = [action.to_dict() for action in game.actions.all()]
        if game.winner_id == match_dict['players']['left']['player_id']:
            game_dict['winning_side'] = "left"
        elif game.winner_id == match_dict['players']['right']['player_id']:
            game_dict['winning_side'] = "right"
        game_dicts.append(game_dict)

    return TemplateResponse(
        request,
        'matches/match_detail.html',
        dict(
            match = match_dict,
            games = game_dicts,
            harassment_ratios = harassment_ratios,
            base_invasion_ratios = base_invasion_ratios,
            engagements_won = engagements_won,
            tournament = tournament.name,
            collection = collection.name
        )
    )

def create_select_tournament(request):
    tournaments = models.Tournament.objects.all()
    return TemplateResponse(
        request,
        'matches/create_select_tournament.html',
        dict(
            tournaments=tournaments
        )
    )

def create_match(request, tournament):
    left_form = MatchPlayerForm(request.POST or None, prefix="left-player")
    right_form = MatchPlayerForm(request.POST or None, prefix="right-player")
    match_form = MatchForm(request.POST or None, prefix="match")
    game_form = GameForm(request.POST or None, prefix="game")
    match = None
    if match_form.is_valid() and left_form.is_valid() and right_form.is_valid():
        collection, created = models.Collection.objects.get_or_create(
            name = match_form.cleaned_data['collection'],
            tournament_id = tournament
        )
        slug = models.Match.create_slug(
            [left_form.instance.player, right_form.instance.player]
        )
        match, created = models.Match.objects.get_or_create(
            collection = collection,
            slug = slug,
            match_identifier = match_form.cleaned_data['match_identifier']
        )
        if created:
            left_form.instance.match = right_form.instance.match = match
            left_form.instance.side = "left"
            left_form.save()
            right_form.instance.side = "right"
            right_form.save()
        
    if match and game_form.is_valid():
        game_form.instance.match = match 
        game = game_form.save()
        return HttpResponseRedirect(reverse('stat-keeper', args=[game.id]))
        
    maps = dict((m.id, "%s%s" % (settings.MEDIA_URL, m.map_file))
                for m in models.Map.objects.all())
    maps = simplejson.dumps(maps)

    return TemplateResponse(
        request,
        'matches/game_create.html',
        dict(
            game_form = game_form,
            match_form = match_form,
            left_form = left_form,
            right_form = right_form,
            maps = maps,
        )
    )

def swapsides_game(request, game_id):
    game = models.Game.objects.get(id=game_id)
    should_be_left = game.match.matchplayer_set.filter(side='right')[0]
    should_be_left.side = 'temp'
    should_be_left.save()

    should_be_right = game.match.matchplayer_set.filter(side='left')[0]
    should_be_right.side = 'right'
    should_be_right.save();

    should_be_left.side = 'left';
    should_be_left.save();
    game.action_set.all().delete();
    return HttpResponseRedirect(reverse('stat-keeper', args=[game.id]))

def create_next_game(request, game_id):
    last_game = models.Game.objects.get(id=game_id)
    map_id = request.POST.get("game_map")
    new_game = models.Game(
        match_id = last_game.match_id,
        game_number = last_game.game_number + 1,
        game_map_id = map_id
    )
    new_game.save()
    return HttpResponseRedirect(reverse('stat-keeper', args=[new_game.id]))

def change_game_map(request, game_id):
    map_id = request.POST.get("game_map")
    game = models.Game.objects.get(id=game_id)
    game.game_map_id = map_id
    game.action_set.all().delete();
    game.save()
    return HttpResponseRedirect(reverse('stat-keeper', args=[game.id]))

def stat_keeper(request, game_id):
    game = models.Game.objects.get(id=game_id)
    match = game.match
    player_left = match.matchplayer_set.filter(side='left')[0]
    player_right = match.matchplayer_set.filter(side='right')[0]
    maps = dict((m.id, "%s%s" % (settings.MEDIA_URL, m.map_file))
                for m in models.Map.objects.all())
    maps = simplejson.dumps(maps)
    return render_to_response(
        'matches/stat_keeper.html',
        dict(
            game = game,
            map_form = MapForm(),
            maps = maps,
            game_data = simplejson.dumps(game.to_dict()),
            player_left = player_left,
            player_right = player_right,
            player_left_data = simplejson.dumps(player_left.to_dict()),
            player_right_data = simplejson.dumps(player_right.to_dict()),
        ),
        context_instance=RequestContext(request)
    )

@csrf_exempt
def handle_action(request, game_id, action_id=None): 
    if request.method == "POST":
        return create_action(request, game_id)
    elif request.method == "PUT":
        return save_action(request, game_id, action_id)
    elif request.method == "GET":
        #Do get here
        pass
    elif request.method == "GET":
        return delete_action(request, game_id, action_id)

def delete_action(request, game_id, action_id):
    action = models.Action.objects.get(id = action_id)
    models.Game.objects.get(id=game_id).delete()
    return HttpResponse(simplejson.dumps({'deleted':True}))

def save_action(request, game_id, action_id):
    request.PUT = QueryDict(request.raw_post_data)
    action_data = simplejson.loads(request.PUT.get("model"))
    action = models.Action.objects.get(id = action_data['id'])
    game = models.Game.objects.get(id=game_id)
    for key in action_data:
        if key not in ['id', 'side', 'winner', 'results', 'position']:
            setattr(action, key, action_data[key])
        elif key == 'results':
            action.result_list = action_data['results']
        elif key == 'position':
            action.position_dict = action_data['position']
        elif key == 'winner' and action_data.get("winner"):
            if action_data["winner"] != "tie":
                action.winner = models.MatchPlayer.objects.get(
                    match__id=game.match_id, side=action_data["winner"]
                )
    action.save()
    return HttpResponse(simplejson.dumps(action.to_dict()))
    
def create_action(request, game_id):
    action_data = simplejson.loads(request.POST.get("model"))
    game = models.Game.objects.get(id=game_id)
    side = action_data.get('side')
    if side:
        del action_data['side']
    position = action_data.get('position')
    if position:
        del action_data['position']
    results = action_data.get('results')
    if results:
        del action_data['results']
    action = models.Action(**action_data)
    action.game = game
    action.position_dict = position
    action.result_list = results
    if side:
        action.actor = models.MatchPlayer.objects.get(match=game.match_id, side=side)
    action.save()
    return HttpResponse(simplejson.dumps(action.to_dict()))

@csrf_exempt
def handle_game(request, game_id=None): 
    if request.method == "POST":
        return start_game(request)
    elif request.method == "PUT":
        return save_game(request, game_id)
    elif request.method == "GET":
        #Do get here
        pass

def save_game(request, game_id):
    #save the game
    request.PUT = QueryDict(request.raw_post_data)
    game_data = simplejson.loads(request.PUT.get("model"))
    game = models.Game.objects.get(id = game_id)
    for key in game_data:
        if key == "winner" and game_data['winner'] != game.winner_id:
            winner = game_data['winner']
            legal_winner = False
            for player in game.players.all():
                if player.id == winner:
                    legal_winner = True
            if legal_winner:
                game.winner_id = winner
            else:
                raise AttributeError, "The winner must be one of the players in a game"
                
        elif key not in ['id', 'game_map']:
            setattr(game, key, game_data[key])
    game.save()
    return HttpResponse(simplejson.dumps(game.to_dict())) 

def start_game(request):
    #save the game
    game_data = simplejson.loads(request.POST.get("model"))
    del game_data['game_map']
    game = models.Game(**game_data)
    game.save()
    return HttpResponse(simplejson.dumps(game.to_dict())) 

@csrf_exempt
def handle_game_player(request, game_id, side, player_id=None):
    if request.method == "POST":
        return create_game_player(request, game_id, side)
    return HttpResponse() 
    #TODO fufil other obligations like save and get

def create_game_player(request, game_id, side):
    player_data = simplejson.loads(request.POST.get("model"))
    player_name = player_data['name']
    player, created = models.Player.objects.get_or_create(
        name = player_name,
    )
    game = models.Game.objects.get(id = game_id)
    game_player = models.MatchPlayer.objects.create(
        game = game,
        player = player,
        side = side,
        race = player_data['race']
    )
    return HttpResponse(simplejson.dumps({'id':game_player.id})) 

