# Standard imports
import random

# Pypi imports
import pydantic
import numpy

# Local imports
from global_configuration import DATABASE

class Card(pydantic.BaseModel):
    name: str
    uuid: str
    colors: list
    set_code: str

    def export(self) -> dict:
        return {'name': self.name, 'uuid': self.uuid, 'colors': self.colors, 'set_code': self.set_code}
    
def generate_card(number: int, sheet: dict) -> list:
    """
    Generate a card for the given slot.
    """
    # Retrieving the total weight of the sheet
    total_weight = sheet["totalWeight"]
    # cards_id will contain the uuid of each the cards in the sheet
    cards_id= []
    # weights will contain the cumulative weight of each the cards in the sheet
    weights = []
    for card_id, weight in sheet["cards"].items():
        cards_id.append(card_id)
        if not weights:
            weights.append(weight)
        else:
            weights.append(weights[-1] + weight)
    # Generating random indexes based on the card pool and weights
    cards_index = [random.randint(1, total_weight) for i in range(number)]
    chosen_cards = numpy.searchsorted(weights, cards_index)

    # Get the cards
    card_list = []
    for card_index in chosen_cards:
        card_id = cards_id[card_index]
        # Retrieve infos of the card in the database
        card = Card.model_validate(DATABASE['cards'].find_one({'uuid': card_id}, {'_id': 0}))
        card_list.append(card.name)

    return card_list

def generate_card_balanced(balanced_sheets: dict, number: int) -> list:
    """
    Generate a card for the given slot in a balanced set.
    """
    # Generate sheets to fill this slot    
    match random.choice([1,2,3,4,5]):
        case 1:
            layout = dict(A=2, B=2, C1=6)
        case 2:
            layout = dict(A=3, B=2, C1=5)
        case 3:
            layout = dict(A=4, B=2, C2=4)
        case 4:
            layout = dict(A=4, B=3, C2=3)
        case 5:
            layout = dict(A=4, B=4, C2=2)

    # Select the cards for each sheet
    card_list = []
    for sheet, card_quantity in layout.items():
        starting_index = random.randint(0, len(balanced_sheets[sheet]) - 1)
        for i in range(card_quantity):
            card = balanced_sheets[sheet][(starting_index + i) % len(balanced_sheets[sheet])]
            card_list.append(card)

    # It is possible that the number of cards is higher than the number of cards requested
    if number < len(card_list):
        return random.sample(card_list, number)   
    
    return card_list