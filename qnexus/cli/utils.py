import click
import os
from colorama import Fore
from ..consts import CONFIG_FILE_NAME
from ..config import get_config
from ..client import status as _status
from click import Option, Command
from typing import Any


def is_documented_by(original):
    def wrapper(target):
        target.__doc__ = original.__doc__
        return target

    return wrapper


current_path = os.getcwd()
current_dir = current_path.split(os.sep)[-1]


# QNX utils interface
@click.command()
@is_documented_by(_status)
def status():
    click.echo(_status())


@click.command()
def init():
    """Initialize a new qnexus project."""
    # A project with that name already exists, use that one?
    config = get_config()
    if config:
        raise click.ClickException(
            Fore.GREEN
            + f"Project already initialized: {Fore.YELLOW + config.project_name}"
        )
    if config is None:
        name: str = click.prompt(
            "Enter a project name:",
            default=current_dir,
        )
        click.echo(Fore.GREEN + f"Intialized qnexus project: {name}")


def add_options_to_command(command: Command, model: Any):
    """Add click options using fields of a pydantic model."""
    # Annotate command with options from dict
    for field, value in model.model_fields.items():
        command.params.append(
            Option(
                [f"--{field}"],
                help=value.description,
                show_default=True,
                default=value.default,
                multiple=isinstance(value.default, list),
            )
        )
