"""Component commands: add, list, remove, pins, search."""

import json
import sys

import click

import kicad_sch_api as ksa

from ..utils import load_schematic, parse_position, save_schematic


@click.command()
@click.argument("file")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.option("--lib", default=None, help="Filter by lib_id (e.g. Device:R)")
@click.option("--value", default=None, help="Filter by value")
def cmd_list_components(file: str, as_json: bool, lib: str, value: str) -> None:
    """List all components in schematic."""
    sch = load_schematic(file)

    components = []
    for comp in sch.components:
        if lib and lib not in comp.lib_id:
            continue
        if value and value != comp.value:
            continue
        components.append(comp)

    if as_json:
        data = []
        for comp in components:
            data.append({
                "reference": comp.reference,
                "lib_id": comp.lib_id,
                "value": comp.value,
                "position": {"x": comp.position.x, "y": comp.position.y},
                "rotation": comp.rotation,
                "footprint": comp.footprint,
            })
        click.echo(json.dumps(data, indent=2))
    else:
        if not components:
            click.echo("No components found")
            return
        click.echo(f"{'Ref':<8} {'Lib ID':<30} {'Value':<12} {'Position':<16} {'Rotation'}")
        click.echo("-" * 80)
        for comp in components:
            pos = f"({comp.position.x:.2f}, {comp.position.y:.2f})"
            click.echo(f"{comp.reference:<8} {comp.lib_id:<30} {comp.value:<12} {pos:<16} {comp.rotation}°")


@click.command()
@click.argument("file")
@click.argument("lib_id")
@click.argument("reference")
@click.argument("value")
@click.option("--pos", required=True, help="Position as x,y")
@click.option("--rotation", default=0.0, type=float, help="Rotation in degrees")
@click.option("--footprint", default=None, help="Footprint")
def cmd_add_component(file: str, lib_id: str, reference: str, value: str,
                      pos: str, rotation: float, footprint: str) -> None:
    """Add a component to schematic.

    Example: kicad-sch add circuit.kicad_sch Device:R R1 10k --pos 100,100
    """
    sch = load_schematic(file)
    position = parse_position(pos)

    try:
        comp = sch.components.add(
            lib_id=lib_id,
            reference=reference,
            value=value,
            position=position,
            rotation=rotation,
            footprint=footprint,
        )
        save_schematic(sch, file)
        click.echo(f"Added: {comp.reference} ({lib_id}) at {position}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@click.command()
@click.argument("file")
@click.argument("reference")
def cmd_remove_component(file: str, reference: str) -> None:
    """Remove a component by reference.

    Example: kicad-sch remove circuit.kicad_sch R1
    """
    sch = load_schematic(file)
    try:
        sch.components.remove(reference)
        save_schematic(sch, file)
        click.echo(f"Removed: {reference}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@click.command()
@click.argument("file")
@click.argument("reference")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def cmd_pins(file: str, reference: str, as_json: bool) -> None:
    """Show pins for a component.

    Example: kicad-sch pins circuit.kicad_sch U1
    """
    sch = load_schematic(file)
    try:
        comp = sch.components.get(reference)
    except Exception:
        click.echo(f"Error: Component {reference} not found", err=True)
        sys.exit(1)

    pins = comp.list_pins()

    if as_json:
        click.echo(json.dumps(pins, indent=2))
    else:
        if not pins:
            click.echo(f"{reference}: No pins (symbol library may not be available)")
            return
        click.echo(f"Pins for {reference} ({comp.lib_id}):")
        click.echo(f"{'Pin#':<6} {'Name':<20} {'Type':<12} {'Position'}")
        click.echo("-" * 60)
        for pin in pins:
            pos = pin.get("position", {})
            pos_str = f"({pos.get('x', '?')}, {pos.get('y', '?')})" if pos else "N/A"
            click.echo(f"{pin['number']:<6} {pin['name']:<20} {pin['type']:<12} {pos_str}")


@click.command()
@click.argument("pattern")
@click.option("--limit", default=20, type=int, help="Max results")
def cmd_search(pattern: str, limit: int) -> None:
    """Search symbol library by name.

    Example: kicad-sch search ESP32
    """
    try:
        results = ksa.search_symbols(pattern)
        if not results:
            click.echo(f"No symbols matching '{pattern}'")
            return
        for i, sym in enumerate(results[:limit]):
            click.echo(f"  {sym.lib_id:<40} pins: {len(sym.pins)}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
