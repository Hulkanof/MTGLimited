# Local imports
import models.booster as booster
import models.prerelease as prerelease

# Pypi imports
import click

def new_prerelease(set_name: str, player: int, output: click.Path, online_limited: bool) -> None:
    """
    Generate booster packs for a prerelease event of Magic: The Gathering.
    """
    # Create the booster packs for each player
    if online_limited:
        boosters = booster.create_booster(set_name, player*6)
        prereleases = prerelease.create_prerelease(set_name, player)
        with open(f'{output}/online_limited.txt', 'w') as f:
            booster_content = prerelease.prerelease_formating(boosters, prereleases, online_limited)
            f.write(booster_content)
    else :
        for i in range(player):
            # Create the booster packs
            boosters = booster.create_booster(set_name, 6)
            prereleases = prerelease.create_prerelease(set_name, 1)
            # Save the booster packs
            with open(f'{output}/player_{i+1}.txt', 'w') as f:
                booster_content = prerelease.prerelease_formating(boosters, prereleases)
                f.write(booster_content)