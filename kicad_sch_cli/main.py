"""CLI entry point and command group."""

import logging
import sys

import click

logging.getLogger("kicad_sch_api").setLevel(logging.ERROR)

from . import __version__
from .commands import (
    cmd_add_component,
    cmd_add_junction,
    cmd_add_label,
    cmd_add_wire,
    cmd_create,
    cmd_info,
    cmd_list_components,
    cmd_pins,
    cmd_remove_component,
    cmd_search,
    cmd_to_python,
    cmd_validate,
)


@click.group()
@click.version_option(__version__, prog_name="kicad-sch")
def cli() -> None:
    """KiCad schematic manipulation tool."""


cli.add_command(cmd_create, "create")
cli.add_command(cmd_info, "info")
cli.add_command(cmd_list_components, "list")
cli.add_command(cmd_add_component, "add")
cli.add_command(cmd_remove_component, "remove")
cli.add_command(cmd_add_wire, "wire")
cli.add_command(cmd_add_label, "label")
cli.add_command(cmd_add_junction, "junction")
cli.add_command(cmd_pins, "pins")
cli.add_command(cmd_search, "search")
cli.add_command(cmd_validate, "validate")
cli.add_command(cmd_to_python, "to-python")


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
