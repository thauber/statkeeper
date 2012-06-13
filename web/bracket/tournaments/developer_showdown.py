import bracket.elimination_bracket
import datetime

def create_season():
    bracket.elimination_bracket.bracket_with_names(
        [
            'one',
            'two',
            'three',
            'four',
            'five',
            'six',
            'seven',
            'eight',
            'nine',
            'ten',
            'eleven',
            'twelve',
            'thirteen',
            'fourteen',
            'fiveteen',
            'sixteen',
            'seventeen',
            'eighteen',
            'nineteen',
            'twentyone',
            'twentytwo',
            'twentythree',
            'twentyfour',
            'twentyfive',
        ],
        1,
        datetime.date.today()
    )
