# Standard imports
import json
import random

# Local imports
from cards_handling import sheets
from cards_handling import utils

# Pypi imports
import numpy

def generate_card(slot: str, set_data: dict, cards: dict, number: int) -> list:
    """
    Generate a card for the given slot.
    """
    # Get the card pool
    card_pool = set_data["sheets"].get(slot, None)
    if card_pool is None:
        raise ValueError(f'No card pool found for {slot}.')
    
    # Generating random indexes based on the card pool and weights
    total_weight = card_pool["totalWeight"]
    cards_id= []
    weights = []
    for card_id, weight in card_pool["cards"].items():
        cards_id.append(card_id)
        weights.append(weight)
    cummulative_card_weight = numpy.cumsum(weights)
    cards_index = [random.randint(1, total_weight) for i in range(number)]
    chosen_cards = numpy.searchsorted(cummulative_card_weight, cards_index)

    # Get the cards
    card_list = []
    for card_index in chosen_cards:
        card_id = cards_id[card_index]
        if card_id not in cards:
            raise ValueError(f'Card {card_id} not found in the card list.')
        card_list.append(cards[card_id]["name"])

    return card_list

def boosters_content(boosters_format: list[dict], set_data: dict, cards: dict) -> list:
    """
    Create the content of a booster pack based on the given format.
    """
    # Create the booster content
    packs = []
    for booster_format in boosters_format:
        pack = []
        for slot, number in booster_format.items():
            for i in generate_card(slot, set_data, cards, number):
                pack.append(i)
        packs.append(pack)
    return packs

def select_layout(set_data: dict, number: int ) -> dict:
    """
    Select a layout for the booster pack.
    """
    # Get all needed data
    boosters_total_weight = set_data["boostersTotalWeight"]
    boosters_layouts = set_data['boosters']
    
    # Choose a layout for each booster
    boosters_format = []
    boosters_weight = []
    for layout in boosters_layouts:
        boosters_weight.append(layout['weight'])
    cummulatives_booster_weight = numpy.cumsum(boosters_weight)
    layouts = [random.randint(1, boosters_total_weight) for i in range(number)]
    chosen_layouts = numpy.searchsorted(cummulatives_booster_weight, layouts)
    for layout_index in chosen_layouts:
        boosters_format.append(boosters_layouts[layout_index]['contents'])

    return boosters_format

def is_balanced(data: dict) -> bool:
    """
    Check if the set is balanced.
    """
    # Check if the set is balanced
    if 'play' in data['data']['booster'] : 
        return True
    elif 'draft' in data['data']['booster']:
        booster_name = 'draft'
    else:
        booster_name = 'default'

    balanced = any('balanceColors' in data['data']['booster'][booster_name]['sheets'][sheet] for sheet in data['data']['booster'][booster_name]['sheets'].keys())
    return balanced

def generate_card_balanced(slot: str, set_data: dict, cards: dict, number: int) -> list:
    """
    Generate a card for the given slot in a balanced set.
    """
    # Generate sheets to fill this slot
    balanced_sheets = sheets.generate_sheets(set_data, slot, cards)
    
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

def boosters_balanced_content(boosters_format: list[dict], set_data: dict, cards: dict) -> list:
    """
    Create the content of a booster pack based on the given format for a balanced set.
    """

    # Create the booster content
    packs = []
    for booster_format in boosters_format:
        pack = []
        for slot, number in booster_format.items():
            if 'balanceColors' in set_data['sheets'][slot] or "Common" in slot:
                for i in generate_card_balanced(slot, set_data, cards, number):
                    pack.append(i)
            else:
                for i in generate_card(slot, set_data, cards, number):
                    pack.append(i)
        packs.append(pack)
    return packs

def booster(expansion: str, number: int, force_unbalanced:bool) -> list:
    """
    Create a booster pack for the given expansion.
    """
    # Get the set data
    with open(f'cards_handling/sets/{expansion}.json', 'r') as f:
        data = json.loads(f.read())

    # Get the all booster data
    if 'booster' not in data.get('data', {}):
        raise ValueError(f'{expansion} does not have booster data.')
    
    # Retrieve the set data regatding the booster
    if 'draft' in data['data']['booster']:
        set_data = data['data']['booster']['draft']
    elif 'play' in data['data']['booster']:
        set_data = data['data']['booster']['play']
    else:
        set_data = data['data']['booster']['default']

    # Generate the random seed
    random.seed()

    booster_layouts = select_layout(set_data, number)

    # Create the booster content
    cards = utils.build_card_dict(data["data"]["cards"])
    if force_unbalanced or not is_balanced(data):
        packs = boosters_content(booster_layouts, set_data, cards)
    else :
        packs = boosters_balanced_content(booster_layouts, set_data, cards)

    return packs

def booster_formating(booster: list) -> str:
    """
    Format the booster pack for display.
    """
    # Format the booster pack
    booster_str = ""
    for pack in booster:
        for card in pack:
            booster_str += f'1 {card}\n'
    return booster_str