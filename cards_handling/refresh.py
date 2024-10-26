# Standard Imports
import json
import os
import subprocess
import tempfile

# Pypi Imports
import click
import requests

def download_sets() -> None:
    """
    Download the latest set data from MTGJson.
    """
    # Check if the folder exists
    if not os.path.exists('cards_handling/sets/'):
        os.makedirs('cards_handling/sets/')

    # Make sure the folder is empty
    for file in os.listdir('cards_handling/sets/'):
        os.remove(f'cards_handling/sets/{file}')
    
    # Download the latest set data
    try :
        data = requests.get(url='https://mtgjson.com/api/v5/AllSetFiles.zip', stream=True)
        result = data.content
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f'An error occured while downloading files from MTGJson: {e}')
        return
    
    # Save the data to a file
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = os.path.join(temp_dir, 'AllSetFiles.zip')
        with open(temp_file, 'wb') as f:
            f.write(result)
            try : 
                subprocess.run(['unzip', temp_file, '-d', './cards_handling/sets/'], check=True)
            except subprocess.CalledProcessError as e:
                print(f'An error occured while unzipping the file: {e}')
                return

def remove_non_legal_sets() -> None:
    """
    Remove all sets that do not have booster packs.
    """
    # Get the list of all sets
    sets = os.listdir('cards_handling/sets/')
    
    # Remove all sets that do not have booster packs
    for set_name in sets:
        with open(f'cards_handling/sets/{set_name}', 'r') as f:
            data = json.loads(f.read())
            if 'booster' not in data.get('data', {}):
                os.remove(f'cards_handling/sets/{set_name}')

def refresh_sets(non_legal: bool) -> None:
    """
    Refresh the card and set data with the latest information from MTGJson.
    """
    # Download the latest set data
    download_sets()

    if not non_legal:
        remove_non_legal_sets()

@click.command()
@click.option('--non-legal', is_flag=True, default=False, help='Will remove all sets without booster packs.')
def refresh(non_legal: bool) -> None:
    """
    Refresh the card and set data with the latest information from MTGJson.
    """
    refresh_sets(non_legal)


