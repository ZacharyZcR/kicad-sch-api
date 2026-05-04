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
@click.option("--format", "fmt", default="json", type=click.Choice(["json", "report"]))
def cmd_erc(file: str, output: str, fmt: str) -> None:
    """Run Electrical Rule Check via kicad-cli."""
    import json as json_mod
    import tempfile
    from ..utils import run_kicad_cli, to_win_path, find_kicad_cli

    if not find_kicad_cli():
        click.echo("Error: kicad-cli not found. Set KICAD_CLI env or install KiCad.", err=True)
        sys.exit(1)

    abs_file = str(Path(file).resolve())
    if not output:
        out_dir = str(Path(abs_file).parent)
        output = str(Path(out_dir) / f"{Path(abs_file).stem}-erc.{fmt}")

    args = ["sch", "erc", abs_file, "--format", fmt, "-o", output]
    result = run_kicad_cli(args, abs_file)

    if fmt == "json":
        try:
            with open(output, encoding="utf-8-sig") as f:
                data = json_mod.load(f)
            errors = 0
            warnings = 0
            for sheet in data.get("sheets", []):
                for v in sheet.get("violations", []):
                    sev = v.get("severity", "")
                    desc = v.get("description", "?")
                    click.echo(f"  [{sev}] {desc}")
                    if sev == "error":
                        errors += 1
                    elif sev == "warning":
                        warnings += 1
            click.echo(f"\nERC: {errors} error(s), {warnings} warning(s)")
            if errors > 0:
                sys.exit(1)
        except Exception as e:
            click.echo(result.stdout or result.stderr or str(e))
    else:
        click.echo(result.stdout or result.stderr)
        if result.returncode != 0:
            sys.exit(1)


@click.command()
@click.argument("file")
@click.argument("format", type=click.Choice(["netlist", "bom", "pdf", "svg", "dxf"]))
@click.option("-o", "--output", default=None, help="Output path")
@click.option("--netlist-format", default="kicadsexpr",
              type=click.Choice(["kicadsexpr", "kicadxml", "spice", "spicemodel"]),
              help="Netlist format (only for netlist export)")
@click.option("--bw", is_flag=True, help="Black and white (PDF/SVG only)")
def cmd_export(file: str, format: str, output: str, netlist_format: str, bw: bool) -> None:
    """Export schematic via kicad-cli.

    \b
    Formats:
      netlist  - Electrical netlist
      bom      - Bill of Materials (CSV)
      pdf      - PDF document
      svg      - SVG vector graphics
      dxf      - DXF CAD format
    """
    from ..utils import run_kicad_cli, find_kicad_cli

    if not find_kicad_cli():
        click.echo("Error: kicad-cli not found. Set KICAD_CLI env or install KiCad.", err=True)
        sys.exit(1)

    abs_file = str(Path(file).resolve())
    stem = Path(abs_file).stem

    if format == "netlist":
        out = output or f"{stem}.net"
        args = ["sch", "export", "netlist", abs_file, "-o", out, "--format", netlist_format]
    elif format == "bom":
        out = output or f"{stem}.csv"
        args = ["sch", "export", "bom", abs_file, "-o", out]
    elif format == "pdf":
        out = output or f"{stem}.pdf"
        args = ["sch", "export", "pdf", abs_file, "-o", out]
        if bw:
            args.append("--black-and-white")
    elif format == "svg":
        out = output or "."
        args = ["sch", "export", "svg", abs_file, "-o", out]
        if bw:
            args.append("--black-and-white")
    elif format == "dxf":
        out = output or "."
        args = ["sch", "export", "dxf", abs_file, "-o", out]
    else:
        click.echo(f"Unknown format: {format}", err=True)
        sys.exit(1)

    result = run_kicad_cli(args, abs_file)
    if result.returncode != 0:
        click.echo(f"Error: {result.stderr or result.stdout}", err=True)
        sys.exit(1)
    click.echo(f"Exported: {out}")
