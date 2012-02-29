from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
from django.http import HttpResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt
import utils
import models

def stat_keeper(request):
    return render_to_response(
        'stat_keeper/stat_keeper.html',
        {},
        context_instance=RequestContext(request)
    )

@csrf_exempt
def handle_action(request, match_id, action_id=None): 
    if request.method == "POST":
        return create_action(request, match_id)
    elif request.method == "PUT":
        return save_action(request, match_id, action_id)
    elif request.method == "GET":
        #Do get here
        pass

def save_action(request, match_id, action_id):
    request.PUT = QueryDict(request.raw_post_data)
    action_data = simplejson.loads(request.PUT.get("model"))
    action = models.Action.objects.get(id = action_data['id'])
    for key in action_data:
        if key not in ['id', 'side', 'winner']:
            setattr(action, key, action_data[key])
        elif key is 'winner' and action_data.get("winner"):
            if action_data["winner"] != "tie":
                action.winner = models.MatchPlayer.objects.get(
                    match__id=match_id, side=action_data["winner"]
                )
    action.save()
    return HttpResponse(simplejson.dumps(action.to_dict()))
    
def create_action(request, match_id):
    action_data = simplejson.loads(request.POST.get("model"))
    match = models.Match.objects.get(id=match_id)
    side = action_data['side']
    del action_data['side']
    action = models.Action(**action_data)
    action.match = match
    if side:
        action.actor = models.MatchPlayer.objects.get(match=match, side=side)
    action.save()
    return HttpResponse(simplejson.dumps(action.to_dict()))

@csrf_exempt
def handle_match(request, match_id=None): 
    if request.method == "POST":
        return create_match(request)
    elif request.method == "PUT":
        return save_match(request, match_id)
    elif request.method == "GET":
        #Do get here
        pass

def save_match(request, match_id):
    #save the match
    request.PUT = QueryDict(request.raw_post_data)
    match_data = simplejson.loads(request.PUT.get("model"))
    match = models.Match.objects.get(id = match_id)
    for key in match_data:
        if key is not 'id':
            setattr(match, key, match_data[key])
    match.save()
    return HttpResponse(simplejson.dumps(match.to_dict())) 

def create_match(request):
    #save the match
    match_data = simplejson.loads(request.POST.get("model"))
    match = models.Match(**match_data)
    match.save()
    return HttpResponse(simplejson.dumps(match.to_dict())) 

@csrf_exempt
def handle_match_player(request, match_id, side, player_id=None):
    if request.method == "POST":
        return create_match_player(request, match_id, side)
    return HttpResponse() 
    #TODO fufil other obligations like save and get

def create_match_player(request, match_id, side):
    player_data = simplejson.loads(request.POST.get("model"))
    player_name = player_data['name']
    player, created = models.Player.objects.get_or_create(
        name = player_name,
    )
    match = models.Match.objects.get(id = match_id)
    match_player = models.MatchPlayer.objects.create(
        match = match,
        player = player,
        side = side,
        race = player_data['race']
    )
    return HttpResponse(simplejson.dumps({'id':match_player.id})) 
