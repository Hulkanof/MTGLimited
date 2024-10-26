# Standard imports
import json
import random

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

def build_card_dict(cards: list) -> dict:
    """
    Build a usable dictionary ordered by card uuids.
    """
    card_dict = dict()
    for card in cards:
        card_dict[card['uuid']] = dict(name=card['name'], colors=card['colors'])
    return card_dict

def booster(expansion: str, number: int) -> list:
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
    set_data = data['data']['booster'].get('draft', None)
    if set_data is None:
        set_data = data['data']['booster']['play']

    # Generate the random seed
    random.seed()

    booster_layouts = select_layout(set_data, number)

    # Create the booster content
    cards = build_card_dict(data["data"]["cards"])
    packs = boosters_content(booster_layouts, set_data, cards)

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