# Standard Imports
import os

# Local imports
from utils.refresh import refresh_sets
import limited

# PyPi imports
import click
import dotenv
import pymongo

#------------------------------------------#
# Global Configuration
#------------------------------------------#

dotenv.load_dotenv()

MONGO_CLIENT = pymongo.MongoClient(os.getenv('MONGODB_URL'))
DATABASE = MONGO_CLIENT.mtglimited

#------------------------------------------#
# Run
#------------------------------------------#

@click.group()
def run():
   """
   This tool is build to help you with your limited games of Magic: The Gathering.  

   It is a work in progress and will be updated with new features and improvements.
   """

@click.command()
def refresh() -> None:
   """
   Refresh the card and set data with the latest information from MTGJson.
   """
   refresh_sets()

run.add_command(limited.limited)
run.add_command(limited.prerelease)
run.add_command(limited.chaos)

if __name__ == '__main__':
   run()