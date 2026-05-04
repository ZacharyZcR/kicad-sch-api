"""Shared utilities for CLI commands."""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple

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


_kicad_cli_path: Optional[str] = None


def find_kicad_cli() -> Optional[str]:
    """Find kicad-cli executable, including Windows KiCad from WSL."""
    global _kicad_cli_path
    if _kicad_cli_path is not None:
        return _kicad_cli_path

    env_path = os.environ.get("KICAD_CLI")
    if env_path and Path(env_path).exists():
        _kicad_cli_path = env_path
        return _kicad_cli_path

    native = shutil.which("kicad-cli")
    if native:
        _kicad_cli_path = native
        return _kicad_cli_path

    if _is_wsl():
        for base in [
            "/mnt/c/Users/*/AppData/Local/Programs/KiCad/*/bin/kicad-cli.exe",
        ]:
            import glob
            matches = sorted(glob.glob(base), reverse=True)
            if matches:
                _kicad_cli_path = matches[0]
                return _kicad_cli_path

    _kicad_cli_path = ""
    return None


def _is_wsl() -> bool:
    """Detect if running under WSL."""
    try:
        with open("/proc/version") as f:
            return "microsoft" in f.read().lower()
    except Exception:
        return False


def to_win_path(posix_path: str) -> str:
    """Convert WSL path to Windows path if needed."""
    p = Path(posix_path).resolve()
    s = str(p)
    if s.startswith("/mnt/") and len(s) > 6:
        drive = s[5].upper()
        rest = s[6:].replace("/", "\\")
        return f"{drive}:{rest}"
    return s


def run_kicad_cli(args: List[str], file_path: str) -> subprocess.CompletedProcess:
    """Run kicad-cli with proper path conversion."""
    cli = find_kicad_cli()
    if not cli:
        raise RuntimeError(
            "kicad-cli not found.\n"
            "Set KICAD_CLI=/path/to/kicad-cli or install KiCad."
        )

    is_exe = cli.endswith(".exe")
    if is_exe:
        converted_args = []
        for arg in args:
            if arg.startswith("/") and Path(arg).suffix:
                converted_args.append(to_win_path(arg))
            else:
                converted_args.append(arg)
        cmd = [cli] + converted_args
    else:
        cmd = [cli] + args

    return subprocess.run(cmd, capture_output=True, text=True)
