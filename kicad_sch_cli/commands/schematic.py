"""Schematic-level commands: create, info, validate, to-python."""

import json
import sys
from pathlib import Path

import click

import kicad_sch_api as ksa

from ..utils import load_schematic


@click.command()
@click.argument("name")
@click.option("-o", "--output", default=None, help="Output file path (default: <name>.kicad_sch)")
def cmd_create(name: str, output: str) -> None:
    """Create a new empty schematic."""
    output = output or f"{name}.kicad_sch"
    if Path(output).exists():
        click.confirm(f"{output} already exists, overwrite?", abort=True)
    sch = ksa.create_schematic(name)
    sch.save(output)
    click.echo(f"Created: {output}")


@click.command()
@click.argument("file")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def cmd_info(file: str, as_json: bool) -> None:
    """Show schematic information."""
    sch = load_schematic(file)

    components = list(sch.components)
    wires = list(sch.wires)
    labels = list(sch.labels)
    h_labels = list(sch.hierarchical_labels)

    if as_json:
        data = {
            "file": file,
            "version": sch.version,
            "generator": sch.generator,
            "uuid": sch.uuid,
            "components": len(components),
            "wires": len(wires),
            "labels": len(labels),
            "hierarchical_labels": len(h_labels),
        }
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo(f"File:      {file}")
        click.echo(f"Version:   {sch.version}")
        click.echo(f"Generator: {sch.generator}")
        click.echo(f"UUID:      {sch.uuid}")
        click.echo(f"Components:          {len(components)}")
        click.echo(f"Wires:               {len(wires)}")
        click.echo(f"Labels:              {len(labels)}")
        click.echo(f"Hierarchical Labels: {len(h_labels)}")


@click.command()
@click.argument("file")
def cmd_validate(file: str) -> None:
    """Validate schematic for errors."""
    sch = load_schematic(file)
    try:
        issues = sch.validate()
        if not issues:
            click.echo("OK: No issues found")
        else:
            for issue in issues:
                click.echo(f"  [{issue.severity}] {issue.message}")
            sys.exit(1)
    except Exception as e:
        click.echo(f"Validation error: {e}", err=True)
        sys.exit(1)


@click.command()
@click.argument("file")
@click.option("-o", "--output", default=None, help="Output Python file (default: stdout)")
def cmd_to_python(file: str, output: str) -> None:
    """Convert schematic to Python code."""
    output_path = output or "-"
    try:
        if output_path == "-":
            import io
            buf = io.StringIO()
            ksa.schematic_to_python(file, buf)
            click.echo(buf.getvalue())
        else:
            ksa.schematic_to_python(file, output_path)
            click.echo(f"Generated: {output_path}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
