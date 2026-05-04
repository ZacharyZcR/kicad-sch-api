"""Schematic-level commands: create, info, validate, to-python, erc, export."""

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
    junctions = list(sch.junctions)
    no_connects = list(sch.no_connects)
    nets = list(sch.nets)
    title_block = sch.title_block

    if as_json:
        data = {
            "file": file,
            "version": sch.version,
            "generator": sch.generator,
            "uuid": sch.uuid,
            "title_block": title_block if title_block else None,
            "components": len(components),
            "wires": len(wires),
            "junctions": len(junctions),
            "labels": len(labels),
            "hierarchical_labels": len(h_labels),
            "no_connects": len(no_connects),
            "nets": len(nets),
        }
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo(f"File:                {file}")
        click.echo(f"Version:             {sch.version}")
        click.echo(f"Generator:           {sch.generator}")
        click.echo(f"UUID:                {sch.uuid}")
        if title_block:
            for k, v in title_block.items():
                click.echo(f"Title/{k}:          {v}")
        click.echo(f"Components:          {len(components)}")
        click.echo(f"Wires:               {len(wires)}")
        click.echo(f"Junctions:           {len(junctions)}")
        click.echo(f"Labels:              {len(labels)}")
        click.echo(f"Hierarchical Labels: {len(h_labels)}")
        click.echo(f"No Connects:         {len(no_connects)}")
        click.echo(f"Nets:                {len(nets)}")


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
    try:
        if output:
            ksa.schematic_to_python(file, output)
            click.echo(f"Generated: {output}")
        else:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="r") as tmp:
                tmp_path = tmp.name
            ksa.schematic_to_python(file, tmp_path)
            with open(tmp_path) as f:
                click.echo(f.read())
            Path(tmp_path).unlink(missing_ok=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@click.command()
@click.argument("file")
@click.option("-o", "--output", default=None, help="ERC report output path")
@click.option("--format", "fmt", default="report", type=click.Choice(["json", "report"]))
def cmd_erc(file: str, output: str, fmt: str) -> None:
    """Run Electrical Rule Check.

    Requires kicad-cli or Docker.
    """
    sch = load_schematic(file)
    try:
        kwargs = {"format": fmt}
        if output:
            kwargs["output_path"] = output
        report = sch.run_erc(**kwargs)
        if hasattr(report, "has_errors") and report.has_errors():
            click.echo(f"ERC: {report.error_count} error(s), {report.warning_count} warning(s)")
            if hasattr(report, "violations"):
                for v in report.violations:
                    click.echo(f"  [{v.severity}] {v.message}")
            sys.exit(1)
        else:
            click.echo("ERC: OK")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@click.command()
@click.argument("file")
@click.argument("format", type=click.Choice(["netlist", "bom", "pdf", "svg", "dxf"]))
@click.option("-o", "--output", default=None, help="Output path")
@click.option("--netlist-format", default="kicadsexpr",
              type=click.Choice(["kicadsexpr", "kicadxml", "spice", "spicemodel"]),
              help="Netlist format (only for netlist export)")
@click.option("--bom-fields", default=None, help="BOM fields, comma-separated")
@click.option("--bom-group-by", default=None, help="BOM group by fields, comma-separated")
@click.option("--exclude-dnp", is_flag=True, help="Exclude Do-Not-Populate (BOM only)")
@click.option("--bw", is_flag=True, help="Black and white (PDF/SVG only)")
def cmd_export(file: str, format: str, output: str, netlist_format: str,
               bom_fields: str, bom_group_by: str, exclude_dnp: bool, bw: bool) -> None:
    """Export schematic to various formats.

    \b
    Formats:
      netlist  - Electrical netlist (kicadsexpr/kicadxml/spice)
      bom      - Bill of Materials
      pdf      - PDF document
      svg      - SVG vector graphics
      dxf      - DXF CAD format

    Requires kicad-cli or Docker.
    """
    sch = load_schematic(file)
    try:
        if format == "netlist":
            kwargs = {"format": netlist_format}
            if output:
                kwargs["output_path"] = output
            result = sch.export_netlist(**kwargs)
            click.echo(f"Netlist: {result}")
        elif format == "bom":
            kwargs = {}
            if output:
                kwargs["output_path"] = output
            if bom_fields:
                kwargs["fields"] = [f.strip() for f in bom_fields.split(",")]
            if bom_group_by:
                kwargs["group_by"] = [f.strip() for f in bom_group_by.split(",")]
            if exclude_dnp:
                kwargs["exclude_dnp"] = True
            result = sch.export_bom(**kwargs)
            click.echo(f"BOM: {result}")
        elif format == "pdf":
            kwargs = {}
            if output:
                kwargs["output_path"] = output
            if bw:
                kwargs["black_and_white"] = True
            result = sch.export_pdf(**kwargs)
            click.echo(f"PDF: {result}")
        elif format == "svg":
            kwargs = {}
            if output:
                kwargs["output_dir"] = output
            if bw:
                kwargs["black_and_white"] = True
            result = sch.export_svg(**kwargs)
            click.echo(f"SVG: {result}")
        elif format == "dxf":
            kwargs = {}
            if output:
                kwargs["output_dir"] = output
            result = sch.export_dxf(**kwargs)
            click.echo(f"DXF: {result}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
