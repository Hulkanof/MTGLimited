# Standard Imports
import json
import os
import subprocess
import tempfile

# Pypi Imports
import requests

# Local Imports
from global_configuration import DATABASE
from models.booster import Booster
from models.set import Set
from models.prerelease import PreRelease
from models.card import Card

def download_sets(dir: str) -> None:
    """
    Download the latest set data from MTGJson.
    """
    # Download the latest set data
    try :
        data = requests.get(url='https://mtgjson.com/api/v5/AllSetFiles.zip', stream=True)
        result = data.content
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f'An error occured while downloading files from MTGJson: {e}')
        raise e
    
    # Save the data to a file
    temp_file = os.path.join(dir, 'AllSetFiles.zip')
    with open(temp_file, 'wb') as f:
        f.write(result)
        try : 
            subprocess.run(['unzip', temp_file, '-d', dir], check=True)
            os.remove(temp_file)
        except subprocess.CalledProcessError as e:
            print(f'An error occured while unzipping the file: {e}')
            raise e
        
def update_boosters(set: Set) -> None:
    """
    Update the boosters in the database with the latest information from MTGJson.
    """
    # Get the booster data
    booster_name = set.get_booster()
    boosters_data = set.set_data['data']['booster']

    print(f'-   Adding booster data for {set.code} to the database')
    
    # Add the missing boosters to the database
    booster = Booster(layouts=boosters_data[booster_name]['boosters'], total_weight=boosters_data[booster_name]['boostersTotalWeight'], sheets=boosters_data[booster_name]['sheets'], balance_colors=set.is_balanced(), code=set.code)
    new_booster = dict(booster.export())
    
    DATABASE['boosters'].insert_one(new_booster)

def update_cards(set: Set) -> None:
    """
    Update the cards in the database with the latest information from MTGJson.
    """
    # Get the card data
    cards = set.set_data['data']['cards']
    
    # Retrieve the data from the database
    print(f'-   Adding card data to the database')
    remote_cards = DATABASE['cards'].find({}, {'_id': 0,'uuid': 1})

    # Add the missing cards to the database
    for card in cards:
        if not card['uuid'] in remote_cards:
            card_data = Card(name=card['name'], uuid=card['uuid'], colors=card['colors'], set_code=set.code)
            DATABASE['cards'].insert_one(card_data.export())

def update_prerelease(set: Set) -> None:
    """
    Update the prerelease in the database with the latest information from MTGJson.
    """
    # Get the prerelease data
    prerelease_data = set.set_data['data'].get('booster',{}).get('prerelease', {})
    if not prerelease_data:
        print(f'-   No prerelease data found for {set.code}')
    else :
        # Add the missing prerelease to the database
        print(f'-   Adding prerelease data for {set.code} to the database')
        prerelease = PreRelease(code=set.code, layouts=prerelease_data['boosters'], total_weight=prerelease_data['boostersTotalWeight'], sheets=prerelease_data['sheets'])
        DATABASE['prerelease'].insert_one(prerelease.export())
        
def update_data(dir: str) -> None:
    """
    Update the set data in the database with the latest information from MTGJson.
    """
    # Get the list of all sets
    sets = os.listdir(dir)

    # Retrieve the data from the database
    sets_data = DATABASE['sets'].find({}, {'_id':0 ,'code': 1}).to_list()

    # Add the missing sets to the database
    for set_name in sets:
        # Load the set data
        code = set_name.split('.')[0] 
        print("Considering set : ", code)

        # If the set is not in the database, add it
        if not {'code':code} in sets_data:
            with open(f'{dir}/{set_name}', 'r') as f:
                data = json.loads(f.read())
                set = Set(code=code, set_data=data, legal=None)
                print(f'-   Adding set {code} to the database')
                # Check if the set is legal
                set.check_legal()
                DATABASE['sets'].insert_one(set.export())  
    
                # Update the boosters and prerelease data only if the set is legal
                #if set.legal: 
                    #update_boosters(set)
                    #update_prerelease(set)

                # Update the cards data
                #update_cards(set)

def ensure_database() -> None:
    """
    Ensure the database is created and ready to fill.
    """
    collections = DATABASE.list_collection_names()
    
    # Create the collection if it does not exist
    if 'sets' not in collections:
        DATABASE.create_collection('sets')

    # Create the booster collection if it does not exist
    if 'boosters' not in collections:
        DATABASE.create_collection('boosters')

    # Create the card collection if it does not exist
    if 'cards' not in collections:
        DATABASE.create_collection('cards')

    # Create the prerelease collection if it does not exist
    if 'prerelease' not in collections:
        DATABASE.create_collection('prerelease')

def refresh_sets() -> None:
    """
    Refresh the card and set data with the latest information from MTGJson.
    """
    # Ensure the database is created and ready to fill
    ensure_database()

    # Create a temporary directory to download the data
    with tempfile.TemporaryDirectory() as temp_dir:
        # Download the latest set data
        download_sets(temp_dir)
        # Update the set data in the database with the latest information from MTGJson
        update_data(temp_dir)