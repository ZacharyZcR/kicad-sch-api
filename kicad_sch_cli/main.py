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
    cmd_add_no_connect,
    cmd_add_power,
    cmd_add_wire,
    cmd_batch,
    cmd_create,
    cmd_erc,
    cmd_export,
    cmd_info,
    cmd_list_components,
    cmd_net,
    cmd_pins,
    cmd_remove_component,
    cmd_search,
    cmd_to_python,
    cmd_update_component,
    cmd_validate,
    cmd_wire_pins,
)


@click.group()
@click.version_option(__version__, prog_name="kicad-sch")
@click.option("-v", "--verbose", is_flag=True, help="Show debug output")
def cli(verbose: bool) -> None:
    """KiCad schematic manipulation tool."""
    if verbose:
        logging.getLogger("kicad_sch_api").setLevel(logging.DEBUG)


# Schematic lifecycle
cli.add_command(cmd_create, "create")
cli.add_command(cmd_info, "info")
cli.add_command(cmd_validate, "validate")
cli.add_command(cmd_erc, "erc")
cli.add_command(cmd_export, "export")
cli.add_command(cmd_to_python, "to-python")

# Component operations
cli.add_command(cmd_add_component, "add")
cli.add_command(cmd_update_component, "update")
cli.add_command(cmd_remove_component, "remove")
cli.add_command(cmd_list_components, "list")
cli.add_command(cmd_pins, "pins")
cli.add_command(cmd_search, "search")

# Connectivity
cli.add_command(cmd_add_wire, "wire")
cli.add_command(cmd_wire_pins, "wire-pins")
cli.add_command(cmd_add_label, "label")
cli.add_command(cmd_add_junction, "junction")
cli.add_command(cmd_add_no_connect, "no-connect")
cli.add_command(cmd_add_power, "power")
cli.add_command(cmd_net, "net")

# Batch
cli.add_command(cmd_batch, "batch")


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
