# Local imports
from cards_handling import refresh
from gamemodes import limited
from gamemodes import prerelease

# PyPi imports
import click

#------------------------------------------#
# Run
#------------------------------------------#

@click.group()
def run():
   """
   This tool is build to help you with your limited games of Magic: The Gathering.  

   It is a work in progress and will be updated with new features and improvements.
   """

run.add_command(refresh.refresh)
run.add_command(limited.limited)
run.add_command(prerelease.prerelease)

if __name__ == '__main__':
   run()