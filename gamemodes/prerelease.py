# Local imports
from cards_handling import booster

# Pypi imports
import click

def new_prerelease(set_name: str, player: int, output: click.Path) -> None:
    """
    Generate booster packs for a prerelease event of Magic: The Gathering.
    """
    # Create the booster packs for each player
    for i in range(player):
        # Create the booster packs
        boosters = booster.booster(set_name, 6)
        
        # Save the booster packs
        with open(f'{output}/player_{i+1}.txt', 'w') as f:
            booster_content = booster.booster_formating(boosters)
            f.write(booster_content)
    

@click.command("", no_args_is_help=True)
@click.argument("set_name")
@click.option("--player", default=1, help="Number of players.", show_default=True)
@click.option("--output", required=True, help="Output Directory where the boosters will be saved.", type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True))
def prerelease(set_name: str, player: int, output: click.Path) -> None:
    """
    This command will generate booster packs for a limited game of Magic: The Gathering.
    The command will generate the specified number of boosters for each player.
    The boosters will be saved in the output directory.
    """
    new_prerelease(set_name, player, output)