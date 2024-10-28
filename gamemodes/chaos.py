# Standard Imports
import random

# Local Imports
from cards_handling import booster
from mtglimited import DATABASE

# Pypi imports
import click

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
    print("For each player, the following boosters will be generated:")
    for set_name, number in mapping:
        print(f"{number} booster(s) from {set_name}")
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