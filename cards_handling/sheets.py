# Local imports
from cards_handling import utils
from mtglimited import DATABASE

# Standard Imports
import random

class Color:
    name: str
    cards: list

    def __init__(self, name: str, cards: list):
        self.name = name
        self.cards = cards


def generate_sheets(sheet: dict) -> dict:
    """
    Generate A, B, C1 and C2 sheets for the given slot.
    """
    # Get the sheet data
    sheet_cards = [key for key in sheet['cards'].keys()]
    
    # Generate needed sctructures to generate the sheets
    red = Color('Red', list())
    blue = Color('Blue', list())
    green = Color('Green', list())
    white = Color('White', list())
    black = Color('Black', list())
    total = list()
    for raw_card in sheet_cards:
        card = DATABASE['cards'].find_one({'uuid': raw_card}, {'_id': 0, 'name': 1, 'colors': 1})
        total.append(card['name'])
        match card['colors']:
            case ['R']:
                if card["name"] not in red.cards:
                    red.cards.append(card['name'])
            case ['U']:
                if card["name"] not in blue.cards:
                    blue.cards.append(card['name'])
            case ['G']:
                if card["name"] not in green.cards:
                    green.cards.append(card['name'])
            case ['W']:
                if card["name"] not in white.cards:
                    white.cards.append(card['name'])
            case ['B']:
                if card["name"] not in black.cards:
                    black.cards.append(card['name'])

    # Choose colors for A and B
    colors = [red, blue, green, white, black]
    random.shuffle(colors)

    # Choose the colors for A and B
    a_colors = colors[:3]
    b_colors = colors[3:]

    # Initialize the needed variables
    total_cards = len(sheet_cards)
    card_subdivision = total_cards // 10
    a_cards = {a_colors[0].name : dict(), a_colors[1].name : dict(), a_colors[2].name : dict()}
    c1_cards = dict()
    a_size = card_subdivision
    c1_size = card_subdivision
    b_cards = {b_colors[0].name : dict(), b_colors[1].name : dict()}
    c2_cards = dict()
    b_size = card_subdivision
    c2_size = card_subdivision

    # Choose the cards for A
    for color in colors:
        random.shuffle(color.cards)

    for i in range(a_size):
        for color in a_colors:
            card_added = color.cards.pop()
            a_cards[color.name][card_added] = 2
            total.remove(card_added)

    # Choose the cards for B
    for i in range(b_size):
        for color in b_colors:
            card_added = color.cards.pop()
            b_cards[color.name][card_added] = 3
            total.remove(card_added)

    random.shuffle(total)

    for i in range(c1_size * 3):
        card_added = total.pop()
        c1_cards[card_added] = 2

    for i in range(c2_size * 2):
        card_added = total.pop()
        c2_cards[card_added] = 3

    if len(total) != 0:
        for i in range(len(total)):
            card_added = total.pop()
            if i % 2 == 0:
                c1_cards[card_added] = 2
            else:
                c2_cards[card_added] = 3

    A = []
    B = []
    C1 = []
    C2 = []

    for i in range(a_size * 2):
        for color in a_colors:
            cards = [key for key in a_cards[color.name].keys()]
            if len(cards) == 1:
                index = 0
            else :
                index = random.randint(0, len(cards)-1)
            card = cards[index]
            A.append(card)
            a_cards[color.name][card] -= 1
            if a_cards[color.name][card] == 0:
                a_cards[color.name].pop(card)

    for i in range(b_size * 3):
        for color in b_colors:
            cards = [key for key in b_cards[color.name].keys()]
            if len(cards) == 1:
                index = 0
            else :
                index = random.randint(0, len(cards)-1)
            card = cards[index]
            B.append(card)
            b_cards[color.name][card] -= 1
            if b_cards[color.name][card] == 0:
                b_cards[color.name].pop(card)

    for i in range(c1_size):
        cards = [key for key in c1_cards.keys()]
        if len(cards) == 1:
            index = 0
        else :
            index = random.randint(0, len(cards)-1)
        card = cards[index]
        C1.append(card)
        c1_cards[card] -= 1
        if c1_cards[card] == 0:
            c1_cards.pop(card)

    for i in range(c2_size):
        cards = [key for key in c2_cards.keys()]
        if len(cards) == 1:
            index = 0
        else :
            index = random.randint(0, len(cards)-1)
        card = cards[index]
        C2.append(card)
        c2_cards[card] -= 1
        if c2_cards[card] == 0:
            c2_cards.pop(card)

    return dict(A=A, B=B, C1=C1, C2=C2)