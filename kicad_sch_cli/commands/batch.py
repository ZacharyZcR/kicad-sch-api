"""Batch command: import components and wires from JSON."""

import json
import sys

import click

import kicad_sch_api as ksa

from ..utils import load_schematic, save_schematic


@click.command()
@click.argument("file")
@click.argument("json_file", type=click.Path(exists=True))
def cmd_batch(file: str, json_file: str) -> None:
    """Batch import from JSON file.

    \b
    JSON format:
    {
      "components": [
        {"lib_id": "Device:R", "reference": "R1", "value": "10k", "position": [100, 100]},
        ...
      ],
      "wires": [
        {"start": [100, 100], "end": [150, 100]},
        ...
      ],
      "labels": [
        {"text": "VCC", "position": [100, 50], "type": "global"},
        ...
      ],
      "junctions": [
        {"position": [100, 100]},
        ...
      ]
    }
    """
    sch = load_schematic(file)

    with open(json_file) as f:
        data = json.load(f)

    counts = {"components": 0, "wires": 0, "labels": 0, "junctions": 0}

    for comp in data.get("components", []):
        try:
            pos = tuple(comp["position"]) if isinstance(comp["position"], list) else comp["position"]
            sch.components.add(
                lib_id=comp["lib_id"],
                reference=comp["reference"],
                value=comp.get("value", ""),
                position=pos,
                rotation=comp.get("rotation", 0),
                footprint=comp.get("footprint"),
                unit=comp.get("unit", 1),
            )
            counts["components"] += 1
        except Exception as e:
            click.echo(f"  Warning: component {comp.get('reference', '?')}: {e}", err=True)

    for wire in data.get("wires", []):
        try:
            sch.add_wire(start=tuple(wire["start"]), end=tuple(wire["end"]))
            counts["wires"] += 1
        except Exception as e:
            click.echo(f"  Warning: wire: {e}", err=True)

    for label in data.get("labels", []):
        try:
            pos = tuple(label["position"])
            label_type = label.get("type", "label")
            kwargs = {
                "text": label["text"],
                "position": pos,
                "rotation": label.get("rotation", 0),
            }
            if label.get("shape"):
                kwargs["shape"] = label["shape"]
            if label_type == "global":
                sch.add_global_label(**kwargs)
            elif label_type == "hierarchical":
                sch.add_hierarchical_label(**kwargs)
            else:
                sch.add_label(**kwargs)
            counts["labels"] += 1
        except Exception as e:
            click.echo(f"  Warning: label {label.get('text', '?')}: {e}", err=True)

    for junc in data.get("junctions", []):
        try:
            sch.add_junction(position=tuple(junc["position"]))
            counts["junctions"] += 1
        except Exception as e:
            click.echo(f"  Warning: junction: {e}", err=True)

    save_schematic(sch, file)
    parts = [f"{v} {k}" for k, v in counts.items() if v > 0]
    click.echo(f"Batch imported: {', '.join(parts)}")
