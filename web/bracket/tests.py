"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from matches.models import *
from django.test import TestCase
from bracket.tools import *
from bracket.elimination_bracket import *
import datetime

today = datetime.date.today()

def make_tournament(name):
    league,_ = League.objects.get_or_create(name="Test League")
    season,_ = Season.objects.get_or_create(
        name="Test Season 1",
        league=league,
        start_date=today)
    return Tournament.objects.create(
        name=name,
        season=season,
        start_date=today)

class MatchCreationTest(TestCase):
    def test_dual_collection_creation(self):
        collection_name = "dual collection creation"
        tournament = make_tournament("dual collection creation test")
        create_dual_collection(tournament, collection_name, today, 32)
        self.assertEqual(len(tournament.collection_set.filter(name=collection_name)),1)
        collection = tournament.collection_set.get(name=collection_name)
        self.assertEqual(len(tournament.collection_set.all()), 1)
        self.assertEqual(len(collection.match_set.all()), 5)
        #test the matches exist
        self.assertEqual(len(collection.match_set.filter(match_identifier=1)),1)
        self.assertEqual(len(collection.match_set.filter(match_identifier=2)),1)
        self.assertEqual(len(collection.match_set.filter(match_identifier=3)),1)
        self.assertEqual(len(collection.match_set.filter(match_identifier=4)),1)
        self.assertEqual(len(collection.match_set.filter(match_identifier=5)),1)
        
        match1 = collection.match_set.get(match_identifier=1)
        match2 = collection.match_set.get(match_identifier=2)
        match3 = collection.match_set.get(match_identifier=3)
        match4 = collection.match_set.get(match_identifier=4)
        match5 = collection.match_set.get(match_identifier=5)

        self.assertEqual(len(BracketPath.objects.filter(
                            prev_match=match1,
                            qualifier="winner",
                            next_match=match3)), 1)
        self.assertEqual(len(BracketPath.objects.filter(
                            prev_match=match2,
                            qualifier="winner",
                            next_match=match3)), 1)
        self.assertEqual(len(BracketPath.objects.filter(
                            prev_match=match3,
                            qualifier="loser",
                            next_match=match5)), 1)
        self.assertEqual(len(BracketPath.objects.filter(
                            prev_match=match1,
                            qualifier="loser",
                            next_match=match4)), 1)
        self.assertEqual(len(BracketPath.objects.filter(
                            prev_match=match2,
                            qualifier="loser",
                            next_match=match4)), 1)
        self.assertEqual(len(BracketPath.objects.filter(
                            prev_match=match4,
                            qualifier="winner",
                            next_match=match5)), 1)

    def test_create_match(self):
        tourn = make_tournament("match with paths creation test")
        coll = Collection.objects.create(
            tournament=tourn,
            name="match with paths collection",
            start_date=today,
            player_pool=4,
            group_identifier=4,
        )
        match1 = create_match(coll, 5, match_identifier=1, start_date=today)
        assert match1
        self.assertEqual(match1.collection, coll)
        match2 = create_match(
            coll,
            5,
            [match1],
            ['winner'],
            match_identifier=2,
            start_date=today
        )
        self.assertEqual(len(BracketPath.objects.filter(
                            prev_match=match1,
                            qualifier="winner",
                            next_match=match2)), 1)
        match3 = create_match(
            coll,
            5,
            [match1, match2],
            ['loser', 'winner'],
            match_identifier=3,
            start_date=today
        )
        self.assertEqual(len(BracketPath.objects.filter(
                            prev_match=match1,
                            qualifier="loser",
                            next_match=match3)), 1)
        self.assertEqual(len(BracketPath.objects.filter(
                            prev_match=match2,
                            qualifier="winner",
                            next_match=match3)), 1)

    def test_elimination_bracket_creation(self):
        
        tournament = make_tournament("elimination_bracket_creation")
        create_elimination_bracket(tournament, "Ro %s", 8, 3, today)
        self.assertEqual(len(tournament.collection_set.all()), 3)
        #has a ro8
        self.assertEqual(len(tournament.collection_set.filter(name="Ro 8")), 1)
        #ro8 has 4 matches
        self.assertEqual(
            len(tournament.collection_set.get(name="Ro 8").match_set.all()), 4)
        #has a ro4
        self.assertEqual(len(tournament.collection_set.filter(name="Ro 4")), 1)
        #ro4 has 1 matches
        self.assertEqual(
            len(tournament.collection_set.get(name="Ro 4").match_set.all()), 2)
        #has a ro2
        self.assertEqual(len(tournament.collection_set.filter(name="Ro 2")), 1)
        #ro2 has 1 matches
        self.assertEqual(
            len(tournament.collection_set.get(name="Ro 2").match_set.all()), 1)

        #test collection creation with specified names
        tournament = make_tournament("elimination_bracket_creation2")
        create_elimination_bracket(
            tournament,
            "Ro %s",
            8,
            3,
            today,
            round_names={4:"Semi-Finals"}, 
        )
        self.assertEqual(len(tournament.collection_set.all()), 3)
        self.assertEqual(len(tournament.collection_set.filter(name="Ro 8")), 1)
        self.assertEqual(len(tournament.collection_set.filter(name="Semi-Finals")), 1)
        self.assertEqual(len(tournament.collection_set.filter(name="Ro 2")), 1)

        #test match linking and best_of as list
        tournament = make_tournament("elimination_bracket_creation3")
        create_elimination_bracket(tournament, "Ro %s", 8, [3,3,5], today)
        ro4 = tournament.collection_set.get(name="Ro 4")
        ro2 = tournament.collection_set.get(name="Ro 2")
        championship = ro2.match_set.get(match_identifier=1)
        self.assertEqual(championship.best_of,5)
        for match in ro4.match_set.all():
            self.assertEqual(match.best_of,3)
            self.assertEqual(
                len(BracketPath.objects.filter(
                    prev_match=match,
                    qualifier="winner",
                    next_match=championship)),
                1)

        #test date stuff
        tournament = make_tournament("elimination_bracket_creation4")
        tomorrow = today + datetime.timedelta(days=1)
        two_days = today + datetime.timedelta(days=2)
        three_days = today + datetime.timedelta(days=3)
        dates = ((today, today, tomorrow, tomorrow), two_days, three_days)
        create_elimination_bracket(tournament, "Ro %s", 8, [3,3,5], dates)
        
        #test variable day collections
        ro8 = tournament.collection_set.get(name="Ro 8")
        self.assertEqual(
            len(ro8.match_set.filter(start_date = today)),
            2)
        self.assertEqual(
            len(ro8.match_set.filter(start_date = tomorrow)),
            2)

        #test other days
        ro4 = tournament.collection_set.get(name="Ro 4")
        self.assertEqual(
            len(ro4.match_set.filter(start_date = two_days)),
            2)
        #test other days
        ro2 = tournament.collection_set.get(name="Ro 2")
        self.assertEqual(
            len(ro2.match_set.filter(start_date = three_days)),
            1)

    def test_create_code_s(self):
        create_code_s(
            "Season 2",
            (
                datetime.datetime(2012, 3, 29, 1, 10, 0),
                datetime.datetime(2012, 3, 26, 1, 10, 0),
                datetime.datetime(2012, 3, 28, 1, 10, 0),
                datetime.datetime(2012, 3, 27, 1, 10, 0),
                datetime.datetime(2012, 4, 14, 1, 10, 0),
                datetime.datetime(2012, 4, 12, 1, 10, 0),
                datetime.datetime(2012, 4, 13, 1, 10, 0),
                datetime.datetime(2012, 4, 11, 1, 10, 0),
            ),
            (
                datetime.datetime(2012, 4, 18, 1, 10, 0),
                datetime.datetime(2012, 4, 19, 1, 10, 0),
                datetime.datetime(2012, 4, 25, 1, 10, 0),
                datetime.datetime(2012, 4, 26, 1, 10, 0),
            ),
            (
                datetime.datetime(2012, 5, 2, 1, 10, 0),
                datetime.datetime(2012, 5, 2, 1, 10, 0),
                datetime.datetime(2012, 5, 3, 1, 10, 0),
                datetime.datetime(2012, 5, 3, 1, 10, 0),
            ),
            datetime.datetime(2012, 5, 10, 1, 10, 0),
            datetime.datetime(2012, 5, 19, 1, 10, 0),
        )
        l = League.objects.get(slug="gsl")
        s = Season.objects.get(league=l, name="Season 2")
        t = Tournament.objects.get(season=s, name="Code S")

        self.assertEqual(
            len(t.collection_set.all()), 15)
        self.assertEqual(
            len(Match.objects.filter(collection__tournament=t)), 67)

    def test_create_up_and_downs(self):
        create_up_and_downs(
            "Season 2",
            [6,5,6,6,5],
            (
                datetime.datetime(2012, 3, 12, 1, 10, 0),
                datetime.datetime(2012, 3, 13, 1, 10, 0),
                datetime.datetime(2012, 3, 14, 1, 10, 0),
                datetime.datetime(2012, 3, 15, 1, 10, 0),
                datetime.datetime(2012, 3, 16, 1, 10, 0),
            )
        )
        l = League.objects.get(slug="gsl")
        s = Season.objects.get(league=l, name="Season 2")
        t = Tournament.objects.get(season=s, name="Up and Downs")

        self.assertEqual(
            len(t.collection_set.all()), 5)
        self.assertEqual(
            len(Match.objects.filter(collection__tournament=t)), 65)
        

    def test_create_up_and_downs(self):
        create_code_a(
            "Season 2",
            (
                datetime.datetime(2012, 4, 17, 1, 10, 0),
                datetime.datetime(2012, 4, 17, 1, 10, 0),
                datetime.datetime(2012, 4, 17, 1, 10, 0),
                datetime.datetime(2012, 4, 17, 1, 10, 0),
                datetime.datetime(2012, 4, 17, 1, 10, 0),
                datetime.datetime(2012, 4, 17, 1, 10, 0),
                datetime.datetime(2012, 4, 17, 1, 10, 0),
                datetime.datetime(2012, 4, 17, 1, 10, 0),
                datetime.datetime(2012, 4, 24, 1, 10, 0),
                datetime.datetime(2012, 4, 24, 1, 10, 0),
                datetime.datetime(2012, 4, 24, 1, 10, 0),
                datetime.datetime(2012, 4, 24, 1, 10, 0),
                datetime.datetime(2012, 4, 24, 1, 10, 0),
                datetime.datetime(2012, 4, 24, 1, 10, 0),
                datetime.datetime(2012, 4, 24, 1, 10, 0),
                datetime.datetime(2012, 4, 24, 1, 10, 0),
                datetime.datetime(2012, 5, 1, 1, 10, 0),
                datetime.datetime(2012, 5, 1, 1, 10, 0),
                datetime.datetime(2012, 5, 1, 1, 10, 0),
                datetime.datetime(2012, 5, 1, 1, 10, 0),
                datetime.datetime(2012, 5, 1, 1, 10, 0),
                datetime.datetime(2012, 5, 1, 1, 10, 0),
                datetime.datetime(2012, 5, 1, 1, 10, 0),
                datetime.datetime(2012, 5, 1, 1, 10, 0),
            ),(
                datetime.datetime(2012, 5, 8, 1, 10, 0),
                datetime.datetime(2012, 5, 8, 1, 10, 0),
                datetime.datetime(2012, 5, 8, 1, 10, 0),
                datetime.datetime(2012, 5, 8, 1, 10, 0),
                datetime.datetime(2012, 5, 8, 1, 10, 0),
                datetime.datetime(2012, 5, 8, 1, 10, 0),
                datetime.datetime(2012, 5, 8, 1, 10, 0),
                datetime.datetime(2012, 5, 8, 1, 10, 0),
                datetime.datetime(2012, 5, 9, 1, 10, 0),
                datetime.datetime(2012, 5, 9, 1, 10, 0),
                datetime.datetime(2012, 5, 9, 1, 10, 0),
                datetime.datetime(2012, 5, 9, 1, 10, 0),
                datetime.datetime(2012, 5, 9, 1, 10, 0),
                datetime.datetime(2012, 5, 9, 1, 10, 0),
                datetime.datetime(2012, 5, 9, 1, 10, 0),
                datetime.datetime(2012, 5, 9, 1, 10, 0),
            ),(
                datetime.datetime(2012, 5, 15, 1, 10, 0),
                datetime.datetime(2012, 5, 15, 1, 10, 0),
                datetime.datetime(2012, 5, 15, 1, 10, 0),
                datetime.datetime(2012, 5, 15, 1, 10, 0),
                datetime.datetime(2012, 5, 16, 1, 10, 0),
                datetime.datetime(2012, 5, 16, 1, 10, 0),
                datetime.datetime(2012, 5, 16, 1, 10, 0),
                datetime.datetime(2012, 5, 16, 1, 10, 0),
                datetime.datetime(2012, 5, 17, 1, 10, 0),
                datetime.datetime(2012, 5, 17, 1, 10, 0),
                datetime.datetime(2012, 5, 17, 1, 10, 0),
                datetime.datetime(2012, 5, 17, 1, 10, 0),
            )

        )
        l = League.objects.get(slug="gsl")
        s = Season.objects.get(league=l, name="Season 2")
        t = Tournament.objects.get(season=s, name="Code A")

        self.assertEqual(
            len(t.collection_set.all()), 12)
        self.assertEqual(
            len(Match.objects.filter(collection__tournament=t)), 52)
    
    def test_double_elim(self):
        bracket_with_names(
            ['One','Two','Three','Four','Five','Six','Seven','Eight'],
            1,
            today)
        l = League.objects.get(name = "Developer Showdown")
        s = Season.objects.get(league=l, name="Season 1")
        wb = Tournament.objects.get(season=s, name="Winner's Bracket")
        lb = Tournament.objects.get(season=s, name="Loser's Bracket")

        self.assertEqual(
            len(wb.collection_set.all()), 3)
        self.assertEqual(
            len(Match.objects.filter(collection__tournament=wb)), 7)
        self.assertEqual(
            len(lb.collection_set.all()), 4)
        self.assertEqual(
            len(Match.objects.filter(collection__tournament=lb)), 6)

    def test_double_elim_with_byes(self):
        bracket_with_names(
            ['One','Two','Three','Four','Five','Six','Seven'],
            1,
            today)
        l = League.objects.get(name = "Developer Showdown")
        s = Season.objects.get(league=l, name="Season 1")
        wb = Tournament.objects.get(season=s, name="Winner's Bracket")
        lb = Tournament.objects.get(season=s, name="Loser's Bracket")

        self.assertEqual(
            len(wb.collection_set.all()), 3)
        self.assertEqual(
            len(Match.objects.filter(collection__tournament=wb)), 6)
        self.assertEqual(
            len(lb.collection_set.all()), 4)
        self.assertEqual(
            len(Match.objects.filter(collection__tournament=lb)), 5)

    def test_double_elim_with_complicated_byes(self):
        bracket_with_names(
            ['One','Two','Three','Four','Five','Six'],
            1,
            today)
        l = League.objects.get(name = "Developer Showdown")
        s = Season.objects.get(league=l, name="Season 1")
        wb = Tournament.objects.get(season=s, name="Winner's Bracket")
        lb = Tournament.objects.get(season=s, name="Loser's Bracket")

        self.assertEqual(
            len(wb.collection_set.all()), 3)
        self.assertEqual(
            len(Match.objects.filter(collection__tournament=wb)), 5)
        self.assertEqual(
            len(lb.collection_set.all()), 4)
        empty_collection = lb.collection_set.get(name="Round 1")
        self.assertEqual(
            len(empty_collection.match_set.all()), 0)
        self.assertEqual(
            len(Match.objects.filter(collection__tournament=lb)), 4)

