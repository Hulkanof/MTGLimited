# Local imports
from global_configuration import DATABASE

# Standard Imports
import random

# Pypi imports
import pydantic

class Color(pydantic.BaseModel):
    name: str
    cards: list

class Sheet(pydantic.BaseModel):
    colors: list[Color] | None
    cards: dict

    def ordered_cards(self, size) -> list:
        """
        Return the list of cards in the sheet.
        """
        cards = []
        if self.colors:
            for i in range(size):
                for color in self.colors:
                    card = random.sample([i for i in self.cards[color.name].keys()], 1)[0]
                    cards.append(card)
                    self.cards[color.name][card] -= 1
                    if self.cards[color.name][card] == 0:
                        self.cards[color.name].pop(card)
        else:
            for i in range(size):
                cards.append('')
            for i in range(size // 2):
                card = random.sample([i for i in self.cards.keys()], 1)[0]
                cards[i] = card
                cards[size // 2 + i] = card
                self.cards[card] -= 1
                if self.cards[card] == 0:
                    self.cards.pop(card)
            if '' in cards:
                null_index = cards.index('')
                card = random.sample([i for i in self.cards.keys()], 1)[0]
                cards[null_index] = card
        return cards

def fill_cards_list(sheet: dict) -> tuple[Color, Color, Color, Color, Color, list]:
    # Get the sheet data
    sheet_cards = [key for key in sheet['cards'].keys()]
    
    # Generate needed sctructures to generate the sheets
    red = Color(name='Red', cards=list())
    blue = Color(name='Blue', cards=list())
    green = Color(name='Green', cards=list())
    white = Color(name='White', cards=list())
    black = Color(name='Black', cards=list())
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
    return red, blue, green, white, black, total

def generate_sheets(sheet: dict) -> dict:
    """
    Generate A, B, C1 and C2 sheets for the given slot.
    """
    # Retrieve card list separated by colors
    red, blue, green, white, black, sheet_cards = fill_cards_list(sheet)

    # Choose colors for A and B
    colors = [red, blue, green, white, black]
    random.shuffle(colors)

     # Initialize the needed variables
    a = Sheet(colors=colors[:3], cards={colors[0].name: dict(), colors[1].name: dict(), colors[2].name: dict()})
    b = Sheet(colors=colors[3:], cards={colors[3].name: dict(), colors[4].name: dict()})
    c1 = Sheet(colors=None, cards={})
    c2 = Sheet(colors=None, cards={})
    total_cards = len(sheet_cards)
    card_subdivision = total_cards // 10

    # Shuffle the cards in each color to get a random distribution
    for color in colors:
        random.shuffle(color.cards)

    for i in range(card_subdivision):
        for color in a.colors:
            card_added = color.cards.pop()
            a.cards[color.name][card_added] = 2
            sheet_cards.remove(card_added)
        for color in b.colors:
            card_added = color.cards.pop()
            b.cards[color.name][card_added] = 3
            sheet_cards.remove(card_added)

    # Distribute the remaining cards in C1 and C2
    random.shuffle(sheet_cards)

    for i in range(card_subdivision * 3):
        card_added = sheet_cards.pop()
        c1.cards[card_added] = 2

    for i in range(card_subdivision * 2):
        card_added = sheet_cards.pop()
        c2.cards[card_added] = 3

    # In case there are remaining cards, distribute them in C1 and C2
    if len(sheet_cards) != 0:
        for i in range(len(sheet_cards)):
            card_added = sheet_cards.pop()
            if i % 2 == 0:
                c1.cards[card_added] = 2
            else:
                c2.cards[card_added] = 3

    sheets = {
        'A': a.ordered_cards(card_subdivision * 2),
        'B': b.ordered_cards(card_subdivision * 3),
        'C1': c1.ordered_cards(card_subdivision * 3),
        'C2': c2.ordered_cards(card_subdivision * 2)
    }

    return sheets