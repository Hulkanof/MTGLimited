# Standard imports
import random

# Pypi imports
import pydantic
import numpy

# Local imports
from global_configuration import DATABASE
from models.card import generate_card

class PreRelease(pydantic.BaseModel):
    code: str
    layouts: list
    total_weight: int
    sheets: dict

    def random_layout(self, number: int) -> list[dict]:
        """
        Select random layouts from this prerelease.
        """
        # Boosters_format will contain the layout of each prerelease
        prerelease_format = []
        # Boosters_weight will contain the cummulative weight of each layout for the random selection
        prerelease_weight = []
        for layout in self.layouts:
            if not prerelease_weight:
                prerelease_weight.append(layout['weight'])
            else:   
                prerelease_weight.append(prerelease_weight[-1] + layout['weight'])
        # Choosing a random layout weight for each booster
        random_cards = [random.randint(1, self.total_weight) for i in range(number)]
        # Find the corresponding layout for each random weight
        chosen_layouts = numpy.searchsorted(prerelease_weight, random_cards)
        for layout_index in chosen_layouts:
            prerelease_format.append(self.layouts[layout_index]['contents'])

        return prerelease_format

    def export(self) -> dict:
        return {'code': self.code, 'layouts': self.layouts, 'total_weight': self.total_weight, 'sheets': self.sheets}
    
def prerelease_content(prerelease_format: list[dict], sheets: dict) -> list:
    """
    Create the content of a booster pack based on the given format.
    """
    # Create the booster content
    packs = []
    for booster_format in prerelease_format:
        pack = []
        for slot, number in booster_format.items():
            for i in generate_card(number, sheets[slot]):
                pack.append(i)
        packs.append(pack)
    return packs
    
def create_prerelease(expansion: str, number: int) -> list:
    """
    Create a prerelease pack for the given expansion.
    """
    # Get the set data from the database
    try :
        prereleases = PreRelease.model_validate(DATABASE['prerelease'].find_one({'code': expansion}, {'_id': 0, 'code': 1, 'layouts': 1, 'total_weight': 1, 'sheets': 1}))
    except pydantic.ValidationError as e:
        raise ValueError(f'No prerelease data for {expansion}') from e
    
    # Generate the random seed
    random.seed()

    prerelease_layouts = prereleases.random_layout(number)

    # Create the booster content
    packs = prerelease_content(prerelease_layouts, prereleases.sheets)

    return packs

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
