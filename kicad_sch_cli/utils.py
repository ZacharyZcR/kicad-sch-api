"""Shared utilities for CLI commands."""

import sys
from pathlib import Path
from typing import Tuple

import click

import kicad_sch_api as ksa


def parse_position(value: str) -> Tuple[float, float]:
    """Parse 'x,y' string into tuple."""
    try:
        parts = value.split(",")
        if len(parts) != 2:
            raise ValueError
        return (float(parts[0]), float(parts[1]))
    except (ValueError, IndexError):
        raise click.BadParameter(f"Invalid position: {value} (expected x,y)")


def load_schematic(path: str) -> ksa.Schematic:
    """Load schematic with error handling."""
    p = Path(path)
    if not p.exists():
        click.echo(f"Error: {path} not found", err=True)
        sys.exit(1)
    if not p.suffix == ".kicad_sch":
        click.echo(f"Error: {path} is not a .kicad_sch file", err=True)
        sys.exit(1)
    try:
        return ksa.load_schematic(str(p))
    except Exception as e:
        click.echo(f"Error loading {path}: {e}", err=True)
        sys.exit(1)


def save_schematic(sch: ksa.Schematic, path: str) -> None:
    """Save schematic with error handling."""
    try:
        sch.save(path)
        click.echo(f"Saved: {path}")
    except Exception as e:
        click.echo(f"Error saving {path}: {e}", err=True)
        sys.exit(1)
