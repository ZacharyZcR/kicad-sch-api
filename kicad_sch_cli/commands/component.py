"""Component commands: add, list, remove, update, pins, search."""

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
@click.option("--sort", "sort_by", default="ref",
              type=click.Choice(["ref", "lib", "value", "x", "y"]),
              help="Sort order")
def cmd_list_components(file: str, as_json: bool, lib: str, value: str, sort_by: str) -> None:
    """List all components in schematic."""
    sch = load_schematic(file)

    components = []
    for comp in sch.components:
        if lib and lib not in comp.lib_id:
            continue
        if value and value != comp.value:
            continue
        components.append(comp)

    sort_keys = {
        "ref": lambda c: c.reference,
        "lib": lambda c: c.lib_id,
        "value": lambda c: c.value,
        "x": lambda c: c.position.x,
        "y": lambda c: c.position.y,
    }
    components.sort(key=sort_keys[sort_by])

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
        click.echo(f"\nTotal: {len(components)}")


@click.command()
@click.argument("file")
@click.argument("lib_id")
@click.argument("reference")
@click.argument("value")
@click.option("--pos", required=True, help="Position as x,y")
@click.option("--rotation", default=0.0, type=float, help="Rotation in degrees")
@click.option("--footprint", default=None, help="Footprint")
@click.option("--unit", default=1, type=int, help="Unit number for multi-unit components")
def cmd_add_component(file: str, lib_id: str, reference: str, value: str,
                      pos: str, rotation: float, footprint: str, unit: int) -> None:
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
            unit=unit,
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
@click.option("--pos", default=None, help="New position as x,y")
@click.option("--move", "offset", default=None, help="Translate by dx,dy")
@click.option("--rotation", default=None, type=float, help="Set rotation (degrees)")
@click.option("--rotate", default=None, type=float, help="Rotate by angle (cumulative)")
@click.option("--value", default=None, help="Set value")
@click.option("--footprint", default=None, help="Set footprint")
@click.option("--set-prop", multiple=True, help="Set property as name=value")
def cmd_update_component(file: str, reference: str, pos: str, offset: str,
                         rotation: float, rotate: float, value: str,
                         footprint: str, set_prop: tuple) -> None:
    """Update a component's properties.

    \b
    Examples:
      kicad-sch update circuit.kicad_sch R1 --value 4.7k
      kicad-sch update circuit.kicad_sch U1 --pos 120,80
      kicad-sch update circuit.kicad_sch U1 --rotate 90
      kicad-sch update circuit.kicad_sch R1 --set-prop MPN=RC0603FR-0710KL
    """
    sch = load_schematic(file)
    try:
        comp = sch.components.get(reference)
    except Exception:
        click.echo(f"Error: Component {reference} not found", err=True)
        sys.exit(1)

    changes = []

    if pos:
        p = parse_position(pos)
        comp.move(p[0], p[1])
        changes.append(f"position -> {p}")

    if offset:
        d = parse_position(offset)
        comp.translate(d[0], d[1])
        changes.append(f"translate ({d[0]:+}, {d[1]:+})")

    if rotation is not None:
        comp.rotation = rotation
        changes.append(f"rotation -> {rotation}°")

    if rotate is not None:
        comp.rotate(rotate)
        changes.append(f"rotated +{rotate}°")

    if value is not None:
        comp.value = value
        changes.append(f"value -> {value}")

    if footprint is not None:
        comp.footprint = footprint
        changes.append(f"footprint -> {footprint}")

    for prop_str in set_prop:
        if "=" not in prop_str:
            click.echo(f"Error: Invalid property format: {prop_str} (expected name=value)", err=True)
            sys.exit(1)
        name, val = prop_str.split("=", 1)
        comp.set_property(name, val)
        changes.append(f"{name} = {val}")

    if not changes:
        click.echo("Nothing to update")
        return

    save_schematic(sch, file)
    click.echo(f"Updated {reference}: {', '.join(changes)}")


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
            pos = pin.get("position")
            if pos is None:
                pos_str = "N/A"
            elif isinstance(pos, dict):
                pos_str = f"({pos.get('x', '?')}, {pos.get('y', '?')})"
            elif hasattr(pos, "x"):
                pos_str = f"({pos.x:.2f}, {pos.y:.2f})"
            else:
                pos_str = str(pos)
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
        for sym in results[:limit]:
            click.echo(f"  {sym.lib_id:<40} pins: {len(sym.pins)}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
