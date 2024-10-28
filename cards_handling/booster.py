# Standard imports
import json
import random

# Local imports
from cards_handling import sheets
from cards_handling import utils
from cards_handling.refresh import DATABASE

# Pypi imports
import numpy

def select_layout(layouts: list, total_weight: int, number: int ) -> dict:
    """
    Select a layout for the booster pack.
    """
    # Choose a layout for each booster
    boosters_format = []
    boosters_weight = []
    for layout in layouts:
        boosters_weight.append(layout['weight'])
    cummulatives_booster_weight = numpy.cumsum(boosters_weight)
    random_cards = [random.randint(1, total_weight) for i in range(number)]
    chosen_layouts = numpy.searchsorted(cummulatives_booster_weight, random_cards)
    for layout_index in chosen_layouts:
        boosters_format.append(layouts[layout_index]['contents'])

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

def generate_card(number: int, sheet: dict) -> list:
    """
    Generate a card for the given slot.
    """
    # Generating random indexes based on the card pool and weights
    total_weight = sheet["totalWeight"]
    cards_id= []
    weights = []
    for card_id, weight in sheet["cards"].items():
        cards_id.append(card_id)
        weights.append(weight)
    cummulative_card_weight = numpy.cumsum(weights)
    cards_index = [random.randint(1, total_weight) for i in range(number)]
    chosen_cards = numpy.searchsorted(cummulative_card_weight, cards_index)

    # Get the cards
    card_list = []
    for card_index in chosen_cards:
        card_id = cards_id[card_index]
        card = DATABASE['cards'].find_one({'uuid': card_id}, {'name': 1})
        card_list.append(card['name'])

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

def boosters_content(boosters_format: list[dict], sheets: dict) -> list:
    """
    Create the content of a booster pack based on the given format.
    """
    # Create the booster content
    packs = []
    for booster_format in boosters_format:
        pack = []
        for slot, number in booster_format.items():
            for i in generate_card(number, sheets[slot]):
                pack.append(i)
        packs.append(pack)
    return packs

def boosters_balanced_content(boosters_format: list[dict], sheet: dict) -> list:
    """
    Create the content of a booster pack based on the given format for a balanced set.
    """

    # Create the booster content
    packs = []
    for booster_format in boosters_format:
        pack = []
        for slot, number in booster_format.items():
            if 'balanceColors' in sheet[slot] or "Common" in slot:
                balanced_sheets = sheets.generate_sheets(sheet[slot])
                for i in generate_card_balanced(balanced_sheets,number):
                    pack.append(i)
            else:
                for i in generate_card(number, sheet[slot]):
                    pack.append(i)
        packs.append(pack)
    return packs

def booster(expansion: str, number: int, force_unbalanced: bool) -> list:
    """
    Create a booster pack for the given expansion.
    """
    # Get the set data from the database
    boosters = DATABASE['boosters'].find_one({'code': expansion}, {'_id': 0, 'code': 0})
    if boosters is None:
        raise ValueError(f'{expansion} is not in the database. Please update the database.')
    
    # Generate the random seed
    random.seed()

    booster_layouts = select_layout(boosters['layout'], boosters['total_weight'], number)

    # Create the booster content
    if not boosters['balance_colors'] or force_unbalanced:
        packs = boosters_content(booster_layouts, boosters['sheets'])
    else :
        packs = boosters_balanced_content(booster_layouts, boosters['sheets'])

    return packs

def prerelease(expansion: str, number: int) -> list:
    """
    Create a prerelease pack for the given expansion.
    """
    # Get the set data from the database
    prereleases = DATABASE['prerelease'].find_one({'code': expansion}, {'layouts': 1, 'total_weight': 1, 'sheets': 1})
    if prereleases is None:
        raise ValueError(f'{expansion} is not in the database. Please update the database.')
    
    # Generate the random seed
    random.seed()

    booster_layouts = select_layout(prereleases['layouts'], prereleases['total_weight'], number)

    # Create the booster content
    packs = boosters_content(booster_layouts, prereleases['sheets'])

    return packs

def booster_formating(booster: list, online_draft: bool = False) -> str:
    """
    Format the booster pack for display.
    """
    # Format the booster pack
    booster_str = ""
    for pack in booster:
        for card in pack:
            booster_str += f'1 {card}\n'
        if online_draft:
            booster_str += '\n'
    return booster_str

def prerelease_formating(booster: list, prerelease: list, online_draft: bool = False) -> str:
    """
    Format the prerelease pack for display.
    """
    # Format the prerelease pack
    booster_str = ""
    if not online_draft:
        for pack in booster:
            for card in pack:
                booster_str += f'1 {card}\n'
        for pack in prerelease:
            for card in pack:
                booster_str += f'1 {card}\n'
        booster_str += '\n'
    else:
        for i in range(len(booster) // 6):
            for pack in booster[i:i+6]:
                for card in pack:
                    booster_str += f'1 {card}\n'
            for card in prerelease[i]:
                booster_str += f'1 {card}\n'
            booster_str += '\n'
    return booster_str

def chaos_formating(booster: list) -> str:
    """
    Format the chaos draft for display.
    """
    # Format the chaos draft
    booster_str = ""
    for players_pack in booster:
        for pack in players_pack:
            for card in pack:
                booster_str += f'1 {card}\n'
        booster_str += '\n'
    return booster_str