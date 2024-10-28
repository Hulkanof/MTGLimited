# Local imports
from cards_handling import booster

# Pypi imports
import click

def new_prerelease(set_name: str, player: int, output: click.Path, force_unbalanced: bool, online_limited: bool) -> None:
    """
    Generate booster packs for a prerelease event of Magic: The Gathering.
    """
    # Create the booster packs for each player
    if online_limited:
        boosters = booster.booster(set_name, player*6, force_unbalanced)
        prerelease = booster.prerelease(set_name, player)
        with open(f'{output}/online_limited.txt', 'w') as f:
            booster_content = booster.prerelease_formating(boosters, prerelease, online_limited)
            f.write(booster_content)
    else :
        for i in range(player):
            # Create the booster packs
            boosters = booster.booster(set_name, 6, force_unbalanced)
            prerelease = booster.prerelease(set_name, 1)
            # Save the booster packs
            with open(f'{output}/player_{i+1}.txt', 'w') as f:
                booster_content = booster.prerelease_formating(boosters, prerelease)
                f.write(booster_content)