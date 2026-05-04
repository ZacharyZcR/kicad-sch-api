"""Connectivity commands: wire, label, junction, no-connect, net, power."""

import json
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
@click.argument("ref1")
@click.argument("pin1")
@click.argument("ref2")
@click.argument("pin2")
def cmd_wire_pins(file: str, ref1: str, pin1: str, ref2: str, pin2: str) -> None:
    """Wire two component pins together.

    Example: kicad-sch wire-pins circuit.kicad_sch R1 2 C1 1
    """
    sch = load_schematic(file)
    try:
        sch.add_wire_between_pins(ref1, pin1, ref2, pin2)
        save_schematic(sch, file)
        click.echo(f"Wire: {ref1}.{pin1} -> {ref2}.{pin2}")
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
@click.option("--shape", default=None,
              type=click.Choice(["input", "output", "bidirectional", "tri_state", "passive"]),
              help="Label shape (global/hierarchical only)")
def cmd_add_label(file: str, text: str, pos: str, label_type: str,
                  rotation: float, shape: str) -> None:
    """Add a label to schematic.

    \b
    Examples:
      kicad-sch label circuit.kicad_sch SDA --pos 100,50
      kicad-sch label circuit.kicad_sch VCC --pos 100,50 --type global
      kicad-sch label circuit.kicad_sch DATA --pos 100,50 --type hierarchical --shape bidirectional
    """
    sch = load_schematic(file)
    position = parse_position(pos)

    try:
        kwargs = {"text": text, "position": position, "rotation": rotation}
        if shape:
            kwargs["shape"] = shape
        if label_type == "global":
            sch.add_global_label(**kwargs)
        elif label_type == "hierarchical":
            sch.add_hierarchical_label(**kwargs)
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
        sch.junctions.add(position=position)
        save_schematic(sch, file)
        click.echo(f"Junction at {position}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@click.command()
@click.argument("file")
@click.option("--pos", required=True, help="Position as x,y")
def cmd_add_no_connect(file: str, pos: str) -> None:
    """Add a no-connect marker.

    Example: kicad-sch no-connect circuit.kicad_sch --pos 100,100
    """
    sch = load_schematic(file)
    position = parse_position(pos)

    try:
        sch.no_connects.add(position=position)
        save_schematic(sch, file)
        click.echo(f"No-connect at {position}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@click.command()
@click.argument("file")
@click.argument("lib_id")
@click.option("--pos", required=True, help="Position as x,y")
@click.option("--rotation", default=0.0, type=float, help="Rotation in degrees")
def cmd_add_power(file: str, lib_id: str, pos: str, rotation: float) -> None:
    """Add a power symbol (VCC, GND, etc).

    \b
    Examples:
      kicad-sch power circuit.kicad_sch power:VCC --pos 100,50
      kicad-sch power circuit.kicad_sch power:GND --pos 100,150 --rotation 180
    """
    sch = load_schematic(file)
    position = parse_position(pos)

    if ":" not in lib_id:
        lib_id = f"power:{lib_id}"

    try:
        sym_name = lib_id.split(":")[-1]
        ref = f"FLG{len(list(sch.components)) + 1}"
        sch.components.add(
            lib_id=lib_id,
            reference=ref,
            value=sym_name,
            position=position,
            rotation=rotation,
        )
        save_schematic(sch, file)
        click.echo(f"Power: {sym_name} at {position}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@click.command()
@click.argument("file")
@click.argument("reference")
@click.argument("pin")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def cmd_net(file: str, reference: str, pin: str, as_json: bool) -> None:
    """Query net connectivity for a pin.

    \b
    Examples:
      kicad-sch net circuit.kicad_sch R1 1
      kicad-sch net circuit.kicad_sch U1 3 --json
    """
    sch = load_schematic(file)

    try:
        connected = sch.get_connected_pins(reference, pin)
        pin_pos = sch.get_component_pin_position(reference, pin)

        if as_json:
            data = {
                "source": {"reference": reference, "pin": pin},
                "position": {"x": pin_pos.x, "y": pin_pos.y} if pin_pos else None,
                "connected_pins": [
                    {"reference": ref, "pin": pn} for ref, pn in connected
                ],
            }
            click.echo(json.dumps(data, indent=2))
        else:
            pos_str = f"({pin_pos.x:.2f}, {pin_pos.y:.2f})" if pin_pos else "N/A"
            click.echo(f"{reference}.{pin} at {pos_str}")
            if connected:
                click.echo(f"Connected to:")
                for ref, pn in connected:
                    click.echo(f"  -> {ref}.{pn}")
            else:
                click.echo("  (not connected)")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
