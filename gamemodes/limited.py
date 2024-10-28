# Standard imports
import random

# Local imports 
from cards_handling import booster
from cards_handling.refresh import DATABASE

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

def choose_set(booster_number: int, specific_set: bool) -> list:
    """
    Choose the sets to generate the boosters from.
    """
    boosters_to_generate = []
    if specific_set:
        total_boosters = 0
        while total_boosters < booster_number:
            information = click.prompt("Please enter a set name and the number of boosters to generate separated by a space.").split()
            set_name = information[0]
            number = int(information[1])
            boosters_to_generate.append((set_name, number))
            total_boosters += number
            if total_boosters > booster_number:
                raise ValueError("The total number of boosters to generate is greater than the number of boosters requested.")
            elif total_boosters < booster_number:
                print(f"So far, you have generated {total_boosters} boosters. You need to generate {booster_number - total_boosters} more boosters.")
    else:
        sets = DATABASE['sets'].find({}, {'code': 1}).to_list()
        random.seed()
        random_sets = random.sample(sets, booster_number)
        for sets in random_sets:
            boosters_to_generate.append((sets['code'], 1))

    return boosters_to_generate

def new_chaos(booster_number: int, player: int, output: click.Path, force_unbalanced: bool, online_limited: bool, specific_set: bool) -> None:
    """
    Generate booster packs for a chaos draft of Magic: The Gathering.
    """
    mapping = choose_set(booster_number, specific_set)
    print(mapping)
    if online_limited:
        boosters = []
        for i in range(player):
            player_boosters = []
            for set_name, number in mapping:
                player_boosters.extend(booster.booster(set_name, number, force_unbalanced))
            boosters.append(player_boosters)
        with open(f'{output}/online_limited.txt', 'w') as f:
            booster_content = booster.chaos_formating(boosters)
            f.write(booster_content)
    else:
        for i in range(player):
            boosters = []
            for set_name, number in mapping:
                boosters.extend(booster.booster(set_name, number, force_unbalanced))
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


@click.command("prerelease", no_args_is_help=True)
@click.argument("set_name")
@click.option("--player", default=1, help="Number of players.", show_default=True)
@click.option("--output", required=True, help="Output Directory where the boosters will be saved.", type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True))
@click.option("--force-unbalanced", is_flag=True, default=False, help="Force the boosters to be unbalanced.")
@click.option("--online-limited", is_flag=True, default=False, help="Generate the boosters for an online draft format.")
def prerelease(set_name: str, player: int, output: click.Path, force_unbalanced: bool, online_limited: bool) -> None:
    """
    This command will generate booster packs for a prerelease event of Magic: The Gathering.
    The command will generate the specified number of boosters for each player.
    The boosters will be saved in the output directory.
    """
    new_prerelease(set_name, player, output, force_unbalanced, online_limited)

@click.command("chaos", no_args_is_help=True)
@click.argument("booster_number", type=int)
@click.option("--player", default=1, help="Number of players.", show_default=True)
@click.option("--output", required=True, help="Output Directory where the boosters will be saved.", type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True))
@click.option("--force-unbalanced", is_flag=True, default=False, help="Force the boosters to be unbalanced.")
@click.option("--online-limited", is_flag=True, default=False, help="Generate the boosters for an online draft format.")
@click.option("--specific-set", is_flag=True, default=False, help="Generate the boosters for a specific set. Will ask for the set name.")
def chaos(booster_number: int, player: int, output: click.Path, force_unbalanced: bool, online_limited: bool, specific_set: bool) -> None:
    """
    This command will generate a chaos draft of Magic: The Gathering.
    The command will generate the specified number of boosters for each player.
    The boosters will be saved in the output directory.
    """
    new_chaos(booster_number, player, output, force_unbalanced, online_limited, specific_set)