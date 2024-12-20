# Local imports
import models.booster as booster

# Pypi imports
import click

def new_limited(set_name: str, player: int, number: int, output: click.Path, online_limited: bool) -> None:
    """
    Generate booster packs for a limited game of Magic: The Gathering.
    """
    # Create the booster packs for each player
    if online_limited:
        boosters = booster.create_booster(set_name, player*number)
        
        with open(f'{output}/online_limited.txt', 'w') as f:
            booster_content = booster.booster_formating(boosters, online_limited)
            f.write(booster_content)
    else :
        for i in range(player):
            # Create the booster packs
            boosters = booster.create_booster(set_name, number)

            # Save the booster packs
            with open(f'{output}/player_{i+1}.txt', 'w') as f:
                booster_content = booster.booster_formating(boosters)
                f.write(booster_content)