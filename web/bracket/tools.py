import math
import itertools
from matches.models import *
def create_dual_collections(tournament, nameFormat, identifiers, dates, group):
    for index, identifier in enumerate(identifiers):
        date = get_it_or_index(dates, index)
        create_dual_collection(tournament, nameFormat % (identifier,), date,
                                group)

def create_dual_collection(tournament, name, date, group_id):
    collection = Collection.objects.create(
        tournament=tournament,
        name=name,
        start_date=get_start_date(date),
        player_pool=4,
        group_identifier=group_id)
    match1 = create_match(collection, 3, match_identifier=1, start_date=date)
    match2 = create_match(collection, 3, match_identifier=2, start_date=date)
    winners_match = create_match(
        collection,
        3,
        [match1, match2],
        ["winner", "winner"],
        match_identifier=3,
        start_date=date)
    losers_match = create_match(
        collection,
        3,
        [match1, match2],
        ["loser", "loser"],
        match_identifier=4,
        start_date=date)
    second_place_match = create_match(
        collection,
        3,
        [winners_match, losers_match],
        ["loser", "winner"],
        match_identifier=5,
        start_date=date)

def create_match(collection, best_of, matches=[], qualifiers=[], **kwargs):
    match = Match.objects.create(
        collection=collection,
        best_of=best_of,
        **kwargs
    )

    for prev, qualifier, i in zip(matches, qualifiers, range(len(matches))):
        BracketPath.objects.create(
            prev_match = prev,
            qualifier = qualifier,
            next_match = match,
            identifier = i,
        )
    return match

def create_elimination_bracket(
        tournament,
        name_format,
        size,
        best_of,
        dates,
        losers_bracket=False,
        round_names=None
    ):
    if round_names is None:
        round_names = {}
    if math.log(size,2)%1:
        raise ValueError, "Size must be an exponent of 2, (ie 8, 16, 32)"

    iterations = 0
    round_matches = []
    while (size > 1):
        round_dates = get_it_or_index(dates,iterations)
        last_round_matches = round_matches
        round_matches = []
        if size in round_names:
            round_name = round_names[size]
        else:
            round_name=name_format % (size,)
        collection = Collection.objects.create(
            tournament=tournament,
            name=round_name,
            start_date=get_start_date(round_dates),
            player_pool=size,
            group_identifier=size
        )
        size = size/2
        round_best_of = best_of
        if getattr(round_best_of, '__iter__', False):
            round_best_of = best_of[iterations]
        for i in xrange(size):
            matches = []
            if last_round_matches:
                matches = [
                    last_round_matches[i*2],
                    last_round_matches[i*2+1],
                ]
            match = create_match(
                collection,
                round_best_of,
                matches,
                ["winner", "winner"],
                match_identifier=i+1,
                start_date=get_it_or_index(round_dates, i)
            )
            round_matches.append(match)
        iterations += 1;

def create_round_robins(tournament, name_format, identifiers, sizes, dates,
                        best_of):
    for i,identifier in enumerate(identifiers):
        size = get_it_or_index(sizes, i)
        date = get_it_or_index(dates, i)
        create_round_robin(tournament, name_format % (identifier,), size, date,
                            best_of)

def create_round_robin(tournament, name, size, date, best_of):
    collection = Collection.objects.create(
        tournament=tournament,
        name=name,
        start_date=get_start_date(date),
        player_pool=size,
        group_identifier=size)
    for i, pair in enumerate(itertools.combinations(xrange(size), 2)):
        create_match(collection, best_of, match_identifier=i, start_date=date)

def create_up_and_downs(season_name, sizes, dates, tournament_name=None,
                        league_name=None):
    if tournament_name is None:
        tournament_name = "Up and Downs"
    league,_ = League.objects.get_or_create(name=league_name or "GSL")
    season,_ = Season.objects.get_or_create(name=season_name, league=league,
                defaults={'start_date': get_start_date(dates)})
    tournament = Tournament.objects.create(name=tournament_name, season=season,
                    start_date=get_start_date(dates))
    create_round_robins(tournament, "Group %s", ["A","B","C","D","E"], sizes,
                        dates, 1)

def create_code_a(
    season_name,
    ro48_dates,
    ro32_dates,
    ro24_dates,
    tournament_name=None,
    league_name=None):
    if tournament_name is None:
        tournament_name = "Code A"
    league,_ = League.objects.get_or_create(name=league_name or "GSL")
    season,_ = Season.objects.get_or_create(name=season_name, league=league,
                defaults={'start_date': get_start_date(ro48_dates)})
    tournament = Tournament.objects.create(name=tournament_name, season=season,
                    start_date=get_start_date(ro48_dates))
    ro48_date_iter = ro48_dates.__iter__()
    ro32_date_iter = ro32_dates.__iter__()
    ro24_date_iter = ro24_dates.__iter__()
    for i in xrange(1,5):
        matches=[]

        first_match_date = ro48_date_iter.next()
        collection = Collection.objects.create(
            tournament=tournament,
            name="Ro 48 Bracket %s" % (i,),
            start_date=first_match_date,
            player_pool=12,
            group_identifier=48)
        matches.append(create_match(collection, 3, match_identifier=1,
                        start_date=first_match_date))
        matches.append(create_match(collection, 3, match_identifier=2,
                        start_date=ro48_date_iter.next()))
        matches.append(create_match(collection, 3, match_identifier=3,
                        start_date=ro48_date_iter.next()))
        matches.append(create_match(collection, 3, match_identifier=4,
                        start_date=ro48_date_iter.next()))
        matches.append(create_match(collection, 3, match_identifier=5,
                        start_date=ro48_date_iter.next()))
        matches.append(create_match(collection, 3, match_identifier=6,
                        start_date=ro48_date_iter.next()))

        first_match_date = ro32_date_iter.next()
        collection = Collection.objects.create(
            tournament=tournament,
            name="Ro 32 Bracket %s" % (i,),
            start_date=first_match_date,
            player_pool=8,
            group_identifier=32)

        matches.append(create_match(collection, 3, match_identifier=1,
                        start_date=first_match_date,
                        matches=[matches[0],matches[1]],
                        qualifiers=['winner','winner']))
        matches.append(create_match(collection, 3, match_identifier=2,
                        start_date=ro32_date_iter.next(),
                        matches=[matches[2],matches[3]],
                        qualifiers=['winner','winner']))
        matches.append(create_match(collection, 3, match_identifier=3,
                        start_date=ro32_date_iter.next(),
                        matches=[matches[4]],
                        qualifiers=['winner','winner']))
        matches.append(create_match(collection, 3, match_identifier=4,
                        start_date=ro32_date_iter.next(),
                        matches=[matches[5]],
                        qualifiers=['winner','winner']))

        first_match_date = ro24_date_iter.next()
        collection = Collection.objects.create(
            tournament=tournament,
            name="Ro 24 Bracket %s" % (i,),
            start_date=first_match_date,
            player_pool=6,
            group_identifier=24)

        matches.append(create_match(collection, 3, match_identifier=1,
                        start_date=first_match_date,
                        matches=[matches[6]],
                        qualifiers=['winner','winner']))
        matches.append(create_match(collection, 3, match_identifier=2,
                        start_date=ro24_date_iter.next(),
                        matches=[matches[7]],
                        qualifiers=['winner','winner']))
        matches.append(create_match(collection, 3, match_identifier=3,
                        start_date=ro24_date_iter.next(),
                        matches=[matches[8],matches[9]],
                        qualifiers=['winner','winner']))

            
def create_code_s(
    season_name,
    ro32_dates,
    ro16_dates,
    ro8_dates,
    ro4_date,
    ro2_date,
    tournament_name=None,
    league_name=None):
    if tournament_name is None:
        tournament_name = "Code S"
    league,_ = League.objects.get_or_create(name=league_name or "GSL")
    season,_ = Season.objects.get_or_create(name=season_name, league=league,
                defaults={'start_date': get_start_date(ro32_dates)})
    tournament = Tournament.objects.create(name=tournament_name, season=season,
                    start_date=get_start_date(ro32_dates))
    create_dual_collections(
        tournament,
        "Ro 32 Group %s",
        ["A", "B", "C", "D", "E", "F", "G", "H"],
        ro32_dates,
        32)
    create_dual_collections(
        tournament,
        "Ro 16 Group %s",
        ["A", "B", "C", "D"],
        ro16_dates,
        16)
    create_elimination_bracket(
        tournament,
        "Ro %s",
        8,
        [5,5,7],
        [ro8_dates, ro4_date, ro2_date],
        round_names={4: 'Semi-Finals', 2:'Championship'}
    )

def get_it_or_index(dates, i):
    if getattr(dates, '__iter__', False):
        return dates[i]
    return dates

def get_start_date(dates):
    if getattr(dates, '__iter__', False):
        return min([get_start_date(date) for date in dates])
    return dates
