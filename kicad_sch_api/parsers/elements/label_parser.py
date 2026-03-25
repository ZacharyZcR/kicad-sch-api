"""
Label and hierarchical label elements parser for KiCAD schematics.

Handles parsing and serialization of Label and hierarchical label elements.
"""

import logging
from typing import Any, Dict, List, Optional

import sexpdata

from ...core.config import config
from ..base import BaseElementParser

logger = logging.getLogger(__name__)


class LabelParser(BaseElementParser):
    """Parser for Label and hierarchical label elements."""

    def __init__(self):
        """Initialize label parser."""
        super().__init__("label")

    def _parse_label(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a label definition."""
        # Label format: (label "text" (at x y rotation) (effects ...) (uuid ...))
        if len(item) < 2:
            return None

        label_data = {
            "text": str(item[1]),  # Label text is second element
            "position": {"x": 0, "y": 0},
            "rotation": 0,
            "size": config.defaults.font_size,
            "justify_h": "left",
            "justify_v": "bottom",
            "uuid": None,
        }

        for elem in item[2:]:  # Skip label keyword and text
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0]) if isinstance(elem[0], sexpdata.Symbol) else None

            if elem_type == "at":
                # Parse position: (at x y rotation)
                if len(elem) >= 3:
                    label_data["position"] = {"x": float(elem[1]), "y": float(elem[2])}
                if len(elem) >= 4:
                    label_data["rotation"] = float(elem[3])

            elif elem_type == "effects":
                # Parse effects for font size and justification: (effects (font (size x y)) (justify left bottom))
                for effect_elem in elem[1:]:
                    if isinstance(effect_elem, list):
                        effect_type = (
                            str(effect_elem[0])
                            if isinstance(effect_elem[0], sexpdata.Symbol)
                            else None
                        )

                        if effect_type == "font":
                            # Parse font size
                            for font_elem in effect_elem[1:]:
                                if isinstance(font_elem, list) and str(font_elem[0]) == "size":
                                    if len(font_elem) >= 2:
                                        label_data["size"] = float(font_elem[1])

                        elif effect_type == "justify":
                            # Parse justification (e.g., "left bottom", "right top")
                            # Format: (justify left bottom) or (justify right)
                            if len(effect_elem) >= 2:
                                label_data["justify_h"] = str(effect_elem[1])
                            if len(effect_elem) >= 3:
                                label_data["justify_v"] = str(effect_elem[2])

            elif elem_type == "uuid":
                label_data["uuid"] = str(elem[1]) if len(elem) > 1 else None

        return label_data

    def _parse_hierarchical_label(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a hierarchical label definition."""
        # Format: (hierarchical_label "text" (shape input) (at x y rotation) (effects ...) (uuid ...))
        if len(item) < 2:
            return None

        hlabel_data = {
            "text": str(item[1]),  # Hierarchical label text is second element
            "shape": "input",  # input/output/bidirectional/tri_state/passive
            "position": {"x": 0, "y": 0},
            "rotation": 0,
            "size": config.defaults.font_size,
            "justify": "left",
            "uuid": None,
        }

        for elem in item[2:]:  # Skip hierarchical_label keyword and text
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0]) if isinstance(elem[0], sexpdata.Symbol) else None

            if elem_type == "shape":
                # Parse shape: (shape input)
                if len(elem) >= 2:
                    hlabel_data["shape"] = str(elem[1])

            elif elem_type == "at":
                # Parse position: (at x y rotation)
                if len(elem) >= 3:
                    hlabel_data["position"] = {"x": float(elem[1]), "y": float(elem[2])}
                if len(elem) >= 4:
                    hlabel_data["rotation"] = float(elem[3])

            elif elem_type == "effects":
                # Parse effects for font size and justification: (effects (font (size x y)) (justify left))
                for effect_elem in elem[1:]:
                    if isinstance(effect_elem, list):
                        effect_type = (
                            str(effect_elem[0])
                            if isinstance(effect_elem[0], sexpdata.Symbol)
                            else None
                        )

                        if effect_type == "font":
                            # Parse font size
                            for font_elem in effect_elem[1:]:
                                if isinstance(font_elem, list) and str(font_elem[0]) == "size":
                                    if len(font_elem) >= 2:
                                        hlabel_data["size"] = float(font_elem[1])

                        elif effect_type == "justify":
                            # Parse justification (e.g., "left", "right")
                            if len(effect_elem) >= 2:
                                hlabel_data["justify"] = str(effect_elem[1])

            elif elem_type == "uuid":
                hlabel_data["uuid"] = str(elem[1]) if len(elem) > 1 else None

        return hlabel_data

    def _parse_global_label(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a global label definition."""
        # Format: (global_label "text" (shape input) (at x y rotation) (effects (font ...) (justify ...)) (uuid ...))
        if len(item) < 2:
            return None

        glabel_data = {
            "text": str(item[1]),  # Global label text is second element
            "shape": "input",
            "at": [0, 0, 0],  # [x, y, rotation]
            "effects": {
                "font": {"size": [1.27, 1.27], "thickness": 0.254},
                "justify": ["left"],
            },
            "uuid": None,
        }

        for elem in item[2:]:  # Skip global_label keyword and text
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0]) if isinstance(elem[0], sexpdata.Symbol) else None

            if elem_type == "shape":
                # Parse shape: (shape input)
                if len(elem) >= 2:
                    glabel_data["shape"] = str(elem[1])

            elif elem_type == "at":
                # Parse position and rotation: (at x y rotation)
                at_list = [0, 0, 0]
                if len(elem) >= 2:
                    at_list[0] = float(elem[1])
                if len(elem) >= 3:
                    at_list[1] = float(elem[2])
                if len(elem) >= 4:
                    at_list[2] = float(elem[3])
                glabel_data["at"] = at_list

            elif elem_type == "effects":
                # Parse effects: (effects (font (size x y) (thickness t)) (justify left/right))
                for effect_elem in elem[1:]:
                    if isinstance(effect_elem, list):
                        effect_type = (
                            str(effect_elem[0])
                            if isinstance(effect_elem[0], sexpdata.Symbol)
                            else None
                        )

                        if effect_type == "font":
                            # Parse font properties
                            for font_elem in effect_elem[1:]:
                                if isinstance(font_elem, list):
                                    font_prop = str(font_elem[0]) if isinstance(font_elem[0], sexpdata.Symbol) else None
                                    if font_prop == "size" and len(font_elem) >= 3:
                                        glabel_data["effects"]["font"]["size"] = [
                                            float(font_elem[1]),
                                            float(font_elem[2]),
                                        ]
                                    elif font_prop == "thickness" and len(font_elem) >= 2:
                                        glabel_data["effects"]["font"]["thickness"] = float(font_elem[1])

                        elif effect_type == "justify":
                            # Parse justification: (justify left) or (justify right bottom)
                            justify_list = []
                            for j in effect_elem[1:]:
                                justify_list.append(str(j))
                            glabel_data["effects"]["justify"] = justify_list

            elif elem_type == "uuid":
                glabel_data["uuid"] = str(elem[1]) if len(elem) > 1 else None

        return glabel_data

    def _label_to_sexp(self, label_data: Dict[str, Any]) -> List[Any]:
        """Convert local label to S-expression."""
        sexp = [sexpdata.Symbol("label"), label_data["text"]]

        # Add position
        pos = label_data["position"]
        x, y = pos["x"], pos["y"]
        rotation = label_data.get("rotation", 0)

        # Format coordinates properly
        if isinstance(x, float) and x.is_integer():
            x = int(x)
        if isinstance(y, float) and y.is_integer():
            y = int(y)

        sexp.append([sexpdata.Symbol("at"), x, y, rotation])

        # Add effects (font properties and justification)
        size = label_data.get("size", config.defaults.font_size)
        effects = [sexpdata.Symbol("effects")]
        font = [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), size, size]]
        effects.append(font)

        # Use justification from data, defaulting to "left bottom"
        justify_h = label_data.get("justify_h", "left")
        justify_v = label_data.get("justify_v", "bottom")
        effects.append(
            [sexpdata.Symbol("justify"), sexpdata.Symbol(justify_h), sexpdata.Symbol(justify_v)]
        )
        sexp.append(effects)

        # Add UUID
        if "uuid" in label_data:
            sexp.append([sexpdata.Symbol("uuid"), label_data["uuid"]])

        return sexp

    def _hierarchical_label_to_sexp(self, hlabel_data: Dict[str, Any]) -> List[Any]:
        """Convert hierarchical label to S-expression."""
        sexp = [sexpdata.Symbol("hierarchical_label"), hlabel_data["text"]]

        # Add shape
        shape = hlabel_data.get("shape", "input")
        sexp.append([sexpdata.Symbol("shape"), sexpdata.Symbol(shape)])

        # Add position
        pos = hlabel_data["position"]
        x, y = pos["x"], pos["y"]
        rotation = hlabel_data.get("rotation", 0)
        sexp.append([sexpdata.Symbol("at"), x, y, rotation])

        # Add effects (font properties)
        size = hlabel_data.get("size", config.defaults.font_size)
        effects = [sexpdata.Symbol("effects")]
        font = [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), size, size]]
        effects.append(font)

        # Use justification from data if provided, otherwise default to "left"
        justify = hlabel_data.get("justify", "left")
        effects.append([sexpdata.Symbol("justify"), sexpdata.Symbol(justify)])
        sexp.append(effects)

        # Add UUID
        if "uuid" in hlabel_data:
            sexp.append([sexpdata.Symbol("uuid"), hlabel_data["uuid"]])

        return sexp

    def _global_label_to_sexp(self, glabel_data: Dict[str, Any]) -> List[Any]:
        """Convert global label to S-expression."""
        sexp = [sexpdata.Symbol("global_label"), glabel_data["text"]]

        # Add shape
        shape = glabel_data.get("shape", "input")
        sexp.append([sexpdata.Symbol("shape"), sexpdata.Symbol(shape)])

        # Add position with rotation
        at_data = glabel_data.get("at", [0, 0, 0])
        if isinstance(at_data, list) and len(at_data) >= 3:
            x, y, rotation = at_data[0], at_data[1], at_data[2]
        else:
            x, y, rotation = at_data[0], at_data[1], 0 if len(at_data) >= 2 else (0, 0, 0)
        sexp.append([sexpdata.Symbol("at"), x, y, rotation])

        # Add effects (font and justify)
        effects_data = glabel_data.get("effects", {})
        effects = [sexpdata.Symbol("effects")]

        # Font
        font_data = effects_data.get("font", {})
        font_size = font_data.get("size", [1.27, 1.27])
        font = [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), font_size[0], font_size[1]]]
        if "thickness" in font_data:
            font.append([sexpdata.Symbol("thickness"), font_data["thickness"]])
        effects.append(font)

        # Justify
        justify_list = effects_data.get("justify", ["left"])
        if justify_list:
            justify = [sexpdata.Symbol("justify")]
            for j in justify_list:
                justify.append(sexpdata.Symbol(j) if isinstance(j, str) else j)
            effects.append(justify)

        sexp.append(effects)

        # Add UUID
        if "uuid" in glabel_data:
            sexp.append([sexpdata.Symbol("uuid"), glabel_data["uuid"]])

        return sexp
