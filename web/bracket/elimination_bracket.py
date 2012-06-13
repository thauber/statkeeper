import math
import random
from matches.models import *

def bracket_with_names(team_names, best_of, date):
    players = [Player.objects.create(name=name) for name in team_names]
    return bracket_with_teams(players, best_of, date)

def bracket_with_teams(teams, best_of, date):
    # Number of rounds in the winners bracket
    num_teams = len(teams)
    num_rounds = int(math.ceil(math.log(num_teams,2)))
    matches = []
    loser_matches = []
    league = League.objects.create(
        name = "Developer Showdown"
    )
    #TODO tournament identifier
    season = Season.objects.create(
        league = league,
        name = "Season 1",
        start_date = date,
    )
    winners_bracket = Tournament.objects.create(
        season = season,
        name = "Winner's Bracket",
        start_date = date,
    )
    losers_bracket = Tournament.objects.create(
        season = season,
        name = "Loser's Bracket",
        start_date = date,
    )
    championship_bracket = Tournament.objects.create(
        season = season,
        name = "Championship",
        start_date = date,
    )
    for i in xrange(num_rounds):
        last_matches = matches
        matches = []
        last_loser_matches = loser_matches
        loser_matches = []
        # The factor of the current round
        bracket_factor = num_rounds - i
        num_slots = 2 ** bracket_factor
        num_matches = num_slots/2
        if i == 0:
            #first round
            byes_left = num_slots - num_teams
            team_i = iter(teams)
            collection = Collection.objects.create(
                tournament=winners_bracket,
                name="Round %d" % (i+1,),
                start_date=date,
                player_pool=len(teams),
                group_identifier=i)
            for j in xrange(num_matches,0,-1):
                if (byes_left == j) or (j%2 and byes_left):
                    matches.append(team_i.next())
                    byes_left -= 1
                else:
                    match = construct_match(
                        collection,
                        best_of,
                        prevs=[team_i.next(),team_i.next()],
                        match_identifier=j,
                        start_date=date)
                    matches.append(match)
            #Make First Loser rounds
            collection = Collection.objects.create(
                tournament=losers_bracket,
                name="Round 1",
                start_date=date,
                player_pool=len(teams)/2,
                group_identifier=i)
            for j in xrange(num_matches/2):
                relevant = [matches[j*2], matches[j*2+1]]
                prevs = [m for m in relevant if isinstance(m, Match)]
                if len(prevs) == 2:
                    match = construct_match(
                        collection,
                        best_of,
                        prevs=prevs,
                        match_identifier=j,
                        start_date=date)
                    loser_matches.append(('winner',match))
                elif len(prevs) == 1:
                    loser_matches.append(('loser',prevs[0]))
                else:
                    loser_matches.append(None)
        else:
            collection = Collection.objects.create(
                tournament=winners_bracket,
                name="Round %d" % (i+1,),
                start_date=date,
                player_pool=num_matches*2,
                group_identifier=i)
            for j in xrange(num_matches):
                prevs = []
                for last_match in last_matches[j*2:j*2+1]:
                    if isinstance(last_match, Match):
                        prevs.append(('winner', last_match))
                    else:
                        prevs.append(last_match)
                match = construct_match(
                    collection,
                    best_of,
                    prevs=prevs,
                    match_identifier=j,
                    start_date=date)
                matches.append(match)
            #loser round
            collection = Collection.objects.create(
                tournament=losers_bracket,
                name="Round %d" % (i*2,),
                start_date=date,
                player_pool=num_matches*2,
                group_identifier=i*2-1)
            for j in xrange(num_matches):
                prev_loser_match = last_loser_matches[j] 
                if prev_loser_match:
                    prevs = [
                        ('loser', matches[j]),
                        prev_loser_match   
                    ]
                    match = construct_match(
                        collection,
                        best_of,
                        prevs,
                        j,
                        date)
                    loser_matches.append(('winner', match))
                else:
                    loser_matches.append(('loser', matches[j]))
            last_loser_matches = loser_matches
            loser_matches = []
            if (num_matches > 1):
                collection = Collection.objects.create(
                    tournament=losers_bracket,
                    name="Round %d" % (i*2+1,),
                    start_date=date,
                    player_pool=num_matches,
                    group_identifier=i*2)
                for j in xrange(num_matches/2):
                    match = construct_match(
                        collection,
                        best_of,
                        [last_loser_matches[j*2], last_loser_matches[j*2+1]],
                        j,
                        date)
                    loser_matches.append(('winner', match))

def construct_match(collection, best_of, prevs, match_identifier, start_date):
    match = Match.objects.create(
        collection=collection,
        best_of=best_of,
        start_date=start_date,
        match_identifier=match_identifier,
    )
    for i, prev in enumerate(prevs):
        if isinstance(prev, tuple):
            BracketPath.objects.create(
                qualifier = prev[0],
                prev_match = prev[1],
                next_match = match,
                identifier = i,
            )
        elif isinstance(prev, Player):
            MatchPlayer.objects.create(
                player = prev,
                match = match,
                race = 'protoss',
                identifier = i,
                side=['left','right'][i],
            )
    return match
