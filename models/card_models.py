# Pypi Imports
import pydantic

#------------------------------------------#
# Pydantic Models
#------------------------------------------#

class Set(pydantic.BaseModel):
    code: str
    set_data: dict

    def export(self):
        return {'code': self.code}
    
    # Check if the set can be played in limited
    def is_legal(self):
        """
        Check if the set is legal for limited play.
        """
        # If the set does not have a booster, it is not legal
        if 'booster' not in self.set_data.get('data', {}):
            return False
        booster_types = self.set_data['data']['booster'].keys()

        # If the set does not have those booster types, there are only online boosters
        if 'draft' not in booster_types and 'play' not in booster_types and 'default' not in booster_types:
            return False
        return True
    
    # Find the limited booster in the set
    def get_booster(self):
        if 'play' in self.set_data.get('data', {}).get('booster', {}):
            booster = 'play'
        elif 'draft' in self.set_data.get('data', {}).get('booster', {}):
            booster = 'draft'
        else:
            booster = 'default'
        return booster
    
    # Check if the set is balanced
    def is_balanced(self):
        """
        Check if the set has balanced colors.
        """
        # Retrieve the booster to search
        booster_name = self.get_booster()

        # Check every sheet in the booster to see if one is balanced 
        balanced = any('balanceColors' in self.set_data['data']['booster'][booster_name]['sheets'][sheet] for sheet in self.set_data['data']['booster'][booster_name]['sheets'].keys())
        return balanced

class Booster(pydantic.BaseModel):
    layouts: list
    total_weight: int
    sheets: dict
    balance_colors: bool
    code: str

    def export(self):
        return {'layouts': self.layouts, 'total_weight': self.total_weight, 'sheets': self.sheets, 'balance_colors': self.balance_colors, 'code': self.code} 

class Card(pydantic.BaseModel):
    name: str
    uuid: str
    colors: list
    set_code: str

    def export(self):
        return {'name': self.name, 'uuid': self.uuid, 'colors': self.colors, 'set_code': self.set_code}

class PreRelease(pydantic.BaseModel):
    code: str
    layouts: list
    total_weight: int
    sheets: dict

    def export(self):
        return {'code': self.code, 'layouts': self.layouts, 'total_weight': self.total_weight, 'sheets': self.sheets}

#------------------------------------------#