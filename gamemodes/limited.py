# Local imports 
from cards_handling import booster

# Pypi imports
import click

def new_limited(set_name: str, player: int, number: int, output: click.Path, force_unbalanced: bool, online_limited: bool) -> None:
    """
    Generate booster packs for a limited game of Magic: The Gathering.
    """
    # Create the booster packs for each player
    if online_limited:
        boosters = booster.booster(set_name, player*number, force_unbalanced)
        
        with open(f'{output}/online_limited.txt', 'w') as f:
            booster_content = booster.booster_formating(boosters, online_limited)
            f.write(booster_content)
    else :
        for i in range(player):
            # Create the booster packs
            boosters = booster.booster(set_name, number, force_unbalanced)

            # Save the booster packs
            with open(f'{output}/player_{i+1}.txt', 'w') as f:
                booster_content = booster.booster_formating(boosters)
                f.write(booster_content)

@click.command("limited", no_args_is_help=True)
@click.argument("set_name")
@click.option("--player", default=1, help="Number of players.", show_default=True)
@click.option("--number", default=6, help="Number of boosters to generate per player.", show_default=True)
@click.option("--output", required=True, help="Output Directory where the boosters will be saved.", type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True))
@click.option("--force-unbalanced", is_flag=True, default=False, help="Force the boosters to be unbalanced.")
@click.option("--online-limited", is_flag=True, default=False, help="Generate the boosters for an online draft format.")
def limited(set_name: str, player: int, number: int, output: click.Path, force_unbalanced: bool, online_limited: bool) -> None:
    """
    This command will generate booster packs for a limited game of Magic: The Gathering.
    The command will generate the specified number of boosters for each player.
    The boosters will be saved in the output directory.
    """
    new_limited(set_name, player, number, output, force_unbalanced, online_limited)
    