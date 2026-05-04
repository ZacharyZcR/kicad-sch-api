"""Connectivity commands: wire, label, junction."""

import sys

import click

from ..utils import load_schematic, parse_position, save_schematic


@click.command()
@click.argument("file")
@click.argument("start")
@click.argument("end")
def cmd_add_wire(file: str, start: str, end: str) -> None:
    """Add a wire between two points.

    Example: kicad-sch wire circuit.kicad_sch 100,100 150,100
    """
    sch = load_schematic(file)
    start_pos = parse_position(start)
    end_pos = parse_position(end)

    try:
        sch.add_wire(start=start_pos, end=end_pos)
        save_schematic(sch, file)
        click.echo(f"Wire: {start_pos} -> {end_pos}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@click.command()
@click.argument("file")
@click.argument("text")
@click.option("--pos", required=True, help="Position as x,y")
@click.option("--type", "label_type", default="label",
              type=click.Choice(["label", "global", "hierarchical"]),
              help="Label type")
@click.option("--rotation", default=0.0, type=float, help="Rotation in degrees")
def cmd_add_label(file: str, text: str, pos: str, label_type: str, rotation: float) -> None:
    """Add a label to schematic.

    Example: kicad-sch label circuit.kicad_sch VCC --pos 100,50 --type global
    """
    sch = load_schematic(file)
    position = parse_position(pos)

    try:
        if label_type == "global":
            sch.add_global_label(text=text, position=position, rotation=rotation)
        elif label_type == "hierarchical":
            sch.add_hierarchical_label(text=text, position=position, rotation=rotation)
        else:
            sch.add_label(text=text, position=position, rotation=rotation)
        save_schematic(sch, file)
        click.echo(f"Label: {text} ({label_type}) at {position}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@click.command()
@click.argument("file")
@click.option("--pos", required=True, help="Position as x,y")
def cmd_add_junction(file: str, pos: str) -> None:
    """Add a junction point.

    Example: kicad-sch junction circuit.kicad_sch --pos 100,100
    """
    sch = load_schematic(file)
    position = parse_position(pos)

    try:
        sch.add_junction(position=position)
        save_schematic(sch, file)
        click.echo(f"Junction at {position}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
