# Local imports 
from gamemodes.chaos import new_chaos
from gamemodes.prerelease import new_prerelease
from gamemodes.sealed import new_limited

# Pypi imports
import click

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