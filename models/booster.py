# Standard Imports
import random

# Pypi Imports
import numpy
import pydantic

# Local Imports
from cards_handling import sheets
from global_configuration import DATABASE
from models.card import generate_card, generate_card_balanced

class Booster(pydantic.BaseModel):
    layouts: list
    total_weight: int
    sheets: dict
    balance_colors: bool
    code: str

    def random_layout(self, number: int) -> list[dict]:
        """
        Select random layouts from this booster.
        """
        # Boosters_format will contain the layout of each booster
        boosters_format = []
        # Boosters_weight will contain the cummulative weight of each layout for the random selection
        boosters_weight = []
        for layout in self.layouts:
            if not boosters_weight:
                boosters_weight.append(layout['weight'])
            else:   
                boosters_weight.append(boosters_weight[-1] + layout['weight'])
        # Choosing a random layout weight for each booster
        random_cards = [random.randint(1, self.total_weight) for i in range(number)]
        # Find the corresponding layout for each random weight
        chosen_layouts = numpy.searchsorted(boosters_weight, random_cards)
        for layout_index in chosen_layouts:
            boosters_format.append(self.layouts[layout_index]['contents'])

        return boosters_format

    def export(self) -> dict:
        return {'layouts': self.layouts, 'total_weight': self.total_weight, 'sheets': self.sheets, 'balance_colors': self.balance_colors, 'code': self.code} 
    
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
            if 'balanceColors' in sheet[slot] or ("common" in slot.lower() and "uncommon" not in slot.lower()):
                balanced_sheets = sheets.generate_sheets(sheet[slot])
                for i in generate_card_balanced(balanced_sheets, number):
                    pack.append(i)
            else:
                for i in generate_card(number, sheet[slot]):
                    pack.append(i)
        packs.append(pack)
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

def create_booster(expansion: str, number: int) -> list:
    """
    Create a booster pack for the given expansion.
    """
    # Get the set data from the database
    try:
        boosters = Booster.model_validate(DATABASE['boosters'].find_one({'code': expansion}, {'_id': 0}))
    except pydantic.ValidationError as e:
        raise ValueError(f'No booster data for {expansion}') from e
    
    # Generate the random seed
    random.seed()

    # Choose the layout for each booster
    booster_layouts = boosters.random_layout(number)
    # Create the booster content
    if not boosters.balance_colors:
        packs = boosters_content(booster_layouts, boosters.sheets)
    else :
        packs = boosters_balanced_content(booster_layouts, boosters.sheets)

    return packs