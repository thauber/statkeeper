from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
from django.http import HttpResponse, QueryDict, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.urlresolvers import reverse
import models

from django_ext.http import JSONResponse
from django.template.response import TemplateResponse

from matches.forms import MatchForm, MatchPlayerForm

def create_match(request):
    # match_instance = Match(author = request.user)
    match_form = MatchForm(request.POST or None, prefix='match')
    left_form = MatchPlayerForm(request.POST or None, prefix='left')
    right_form = MatchPlayerForm(request.POST or None, prefix='right')
    if match_form.is_valid() and left_form.is_valid() and right_form.is_valid():
        match_form.instance.collection = match_form.get_collection()
        match = match_form.save()
        left_form.instance.match = match;
        left_form.instance.side = models.Players.left;
        left_form.save();
        right_form.instance.match = match;
        right_form.instance.side = models.Players.right;
        right_form.save();
        return HttpResponseRedirect(reverse('stat-keeper', args=[match.id]))
    maps = dict((m.id, "%s%s" % (settings.MEDIA_URL, m.map_file))
                for m in models.Map.objects.all())
    maps = simplejson.dumps(maps)

        
    return TemplateResponse(
        request,
        'stat_keeper/match_create.html',
        dict(
            match_form = match_form,
            left_form = left_form,
            right_form = right_form,
            maps = maps,
        )
    )

def swapsides_match(request, match_id):
    match = models.Match.objects.get(id=match_id)
    should_be_left = match.matchplayer_set.filter(side='right')[0]
    should_be_left.side = 'temp';
    should_be_left.save()

    should_be_right = match.matchplayer_set.filter(side='left')[0]
    should_be_right.side = 'right';
    should_be_right.save();

    should_be_left.side = 'left';
    should_be_left.save();
    match.action_set.all().delete();
    return HttpResponseRedirect(reverse('stat-keeper', args=[match.id]))

    

def stat_keeper(request, match_id):
    match = models.Match.objects.get(id=match_id)
    player_left = match.matchplayer_set.filter(side='left')[0]
    player_right = match.matchplayer_set.filter(side='right')[0]
    return render_to_response(
        'stat_keeper/stat_keeper.html',
        dict(
            match = match,
            match_data = simplejson.dumps(match.to_dict()),
            player_left_data = simplejson.dumps(player_left.to_dict()),
            player_right_data = simplejson.dumps(player_right.to_dict()),
        ),
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
        return start_match(request)
    elif request.method == "PUT":
        return save_match(request, match_id)
    elif request.method == "GET":
        #Do get here
        pass

def save_match(request, match_id):
    #save the match
    request.PUT = QueryDict(request.raw_post_data)
    match_data = simplejson.loads(request.PUT.get("model"))
    print match_data
    match = models.Match.objects.get(id = match_id)
    for key in match_data:
        if key not in ['id', 'match_map']:
            setattr(match, key, match_data[key])
    match.save()
    return HttpResponse(simplejson.dumps(match.to_dict())) 

def start_match(request):
    #save the match
    match_data = simplejson.loads(request.POST.get("model"))
    del match_data['match_map']
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

