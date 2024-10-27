# Standard Imports
import json
import os
import subprocess
import tempfile

# Pypi Imports
import click
import dotenv
import pymongo
import requests

dotenv.load_dotenv()

MONGO_CLIENT = pymongo.MongoClient(os.getenv('MONGODB_URL'))
DATABASE = MONGO_CLIENT.mtglimited

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
        
def is_balanced(data: dict, booster: str) -> bool:
    """
    Check if the set is balanced.
    """    
    return booster == 'play' or any('balanceColors' in data['data']['booster'][booster]['sheets'][sheet] for sheet in data['data']['booster'][booster]['sheets'].keys()) 

        
def update_boosters(code: str, data: dict) -> None:
    """
    Update the boosters in the database with the latest information from MTGJson.
    """
    # Get the booster data)
    boosters = data['data']['booster']
    if 'draft' in boosters:
        booster = 'draft'
    elif 'play' in boosters:
        booster = 'play'
    else:
        booster = 'default'
    
    # Gather all the booster data
    layout = data['data']['booster'][booster]['boosters']
    total_weight = data['data']['booster'][booster]['boostersTotalWeight']
    sheets = data['data']['booster'][booster]['sheets']
    balance_colors = is_balanced(data, booster)
    new_booster = dict(layout=layout, total_weight=total_weight, sheets=sheets, balance_colors=balance_colors, code=code)
    
    DATABASE['boosters'].insert_one(new_booster)

def update_cards(data: dict) -> None:
    """
    Update the cards in the database with the latest information from MTGJson.
    """
    # Get the card data
    cards = data['data']['cards']
    
    # Retrieve the data from the database
    cards_data = DATABASE['cards'].find({}, {'_id': 0, 'uuid': 1})
    # Add the missing cards to the database
    for card in cards:
        if not card['uuid'] in cards_data:
            name = card['name']
            uuid = card['uuid']
            colors = card['colors']
            set_code = card['setCode']
            card_data = dict(name=name, uuid=uuid, colors=colors, set_code=set_code)
            DATABASE['cards'].insert_one(card_data)
        
def update_data(dir: str) -> None:
    """
    Update the set data in the database with the latest information from MTGJson.
    """
    # Get the list of all sets
    sets = os.listdir(dir)

    # Retrieve the data from the database
    sets_data = DATABASE['sets'].find({}, {'_id': 0, 'code': 1}).to_list()
    print(sets_data)
    # Add the missing sets to the database
    for set_name in sets:
        code = set_name.split('.')[0]
        if not {'code':code} in sets_data:
            print(f'Adding set {code} to the database')
            DATABASE['sets'].insert_one({'code': code})  
            with open(f'{dir}/{set_name}', 'r') as f:
                data = json.loads(f.read())

                # Update the boosters
                update_boosters(code, data)

                # Update the cards
                update_cards(data)

def remove_non_legal_sets(temp_dir: str) -> None:
    """
    Remove all sets that do not have booster packs.
    """
    # Get the list of all sets
    sets = os.listdir(temp_dir)
    
    # Remove all sets that do not have booster packs or have only mtgo or arena booster packs
    for set_name in sets:
        with open(f'{temp_dir}/{set_name}', 'r') as f:
            data = json.loads(f.read())

            if 'booster' not in data.get('data', {}):
                print(f'Removing set {set_name} as it does not have booster data.')
                os.remove(f'{temp_dir}/{set_name}')
            else :
                if 'draft' not in data['data']['booster'] and 'play' not in data['data']['booster'] and 'default' not in data['data']['booster']:
                    print(f'Removing set {set_name} as it does not have booster data.')
                    os.remove(f'{temp_dir}/{set_name}')
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

def refresh_sets() -> None:
    """
    Refresh the card and set data with the latest information from MTGJson.
    """
    # Ensure the database is created and ready to fill
    ensure_database()

    # Create a temporary directory to download the data
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f'Temporary directory created: {temp_dir}')
        # Download the latest set data
        download_sets(temp_dir)

        # Remove all sets that do not have booster packs
        remove_non_legal_sets(temp_dir)

        # Update the set data in the database with the latest information from MTGJson
        update_data(temp_dir)

@click.command()
def refresh() -> None:
    """
    Refresh the card and set data with the latest information from MTGJson.
    """
    refresh_sets()