# Pypi imports
import pydantic

class Set(pydantic.BaseModel):
    code: str
    set_data: dict
    legal: bool | None

    def export(self) -> dict:
        return {'code': self.code, 'legal': self.legal}
    
    # Check if the set can be played in limited
    def check_legal(self) -> None:
        """
        Check if the set is legal for limited play.
        """
        # If the set does not have a booster, it is not legal
        if 'booster' not in self.set_data.get('data', {}):
            self.legal = False
        else :
            booster_types = self.set_data['data']['booster'].keys()

            # If the set does not have those booster types, there are only online boosters
            if 'draft' not in booster_types and 'play' not in booster_types and 'default' not in booster_types:
                self.legal = False
        if self.legal is None:
            self.legal = True
    
    # Find the limited booster in the set
    def get_booster(self) -> str | None:
        booster = None
        if 'play' in self.set_data.get('data', {}).get('booster', {}):
            booster = 'play'
        elif 'draft' in self.set_data.get('data', {}).get('booster', {}):
            booster = 'draft'
        else:
            booster = 'default'
        return booster
    
    # Check if the set is balanced
    def is_balanced(self) -> bool:
        """
        Check if the set has balanced colors.
        """
        # Retrieve the booster to search
        booster_name = self.get_booster()

        if booster_name: 
            # Check every sheet in the booster to see if one is balanced 
            balanced = any('balanceColors' in self.set_data['data']['booster'][booster_name]['sheets'][sheet] for sheet in self.set_data['data']['booster'][booster_name]['sheets'].keys())
            return balanced or booster_name == 'play'
        return False