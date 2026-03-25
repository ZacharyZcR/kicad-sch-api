#!/usr/bin/env python3
"""Tests for hierarchical label shape and justify functionality (Issue #204)."""

import pytest
import kicad_sch_api as ksa


class TestHierarchicalLabelShape:
    """Test shape parameter support for hierarchical labels."""

    def test_hierarchical_label_with_input_shape(self):
        """Test creating hierarchical label with input shape."""
        sch = ksa.create_schematic("TestHLabelShape")
        hlabel = sch.add_hierarchical_label(
            "DATA_IN",
            position=(100, 100),
            shape="input",
            rotation=0
        )

        # Verify shape is set
        hlabel_data = sch._data["hierarchical_labels"][0]
        assert hlabel_data["shape"] == "input"

    def test_hierarchical_label_with_output_shape(self):
        """Test creating hierarchical label with output shape."""
        sch = ksa.create_schematic("TestHLabelShape")
        sch.add_hierarchical_label(
            "DATA_OUT",
            position=(100, 100),
            shape="output",
            rotation=0
        )

        hlabel_data = sch._data["hierarchical_labels"][0]
        assert hlabel_data["shape"] == "output"

    def test_hierarchical_label_with_bidirectional_shape(self):
        """Test creating hierarchical label with bidirectional shape."""
        sch = ksa.create_schematic("TestHLabelShape")
        sch.add_hierarchical_label(
            "DATA_BUS",
            position=(100, 100),
            shape="bidirectional",
            rotation=0
        )

        hlabel_data = sch._data["hierarchical_labels"][0]
        assert hlabel_data["shape"] == "bidirectional"

    def test_hierarchical_label_with_tri_state_shape(self):
        """Test creating hierarchical label with tri_state shape."""
        sch = ksa.create_schematic("TestHLabelShape")
        sch.add_hierarchical_label(
            "CONTROL",
            position=(100, 100),
            shape="tri_state",
            rotation=0
        )

        hlabel_data = sch._data["hierarchical_labels"][0]
        assert hlabel_data["shape"] == "tri_state"

    def test_hierarchical_label_with_passive_shape(self):
        """Test creating hierarchical label with passive shape."""
        sch = ksa.create_schematic("TestHLabelShape")
        sch.add_hierarchical_label(
            "PASSIVE",
            position=(100, 100),
            shape="passive",
            rotation=0
        )

        hlabel_data = sch._data["hierarchical_labels"][0]
        assert hlabel_data["shape"] == "passive"

    def test_hierarchical_label_shape_persists_after_save_load(self):
        """Test that shape persists through save/load cycle."""
        sch = ksa.create_schematic("TestHLabelShape")
        sch.add_hierarchical_label(
            "DATA",
            position=(100, 100),
            shape="bidirectional",
            rotation=0
        )

        # Save and reload
        sch.save("/tmp/test_hlabel_shape.kicad_sch")
        sch2 = ksa.Schematic.load("/tmp/test_hlabel_shape.kicad_sch")

        hlabel_data = sch2._data["hierarchical_labels"][0]
        assert hlabel_data["shape"] == "bidirectional"


class TestHierarchicalLabelJustify:
    """Test automatic justify calculation for hierarchical labels."""

    def test_hierarchical_label_justify_0deg(self):
        """Test justify is 'left' for 0° rotation."""
        sch = ksa.create_schematic("TestHLabelJustify")
        sch.add_hierarchical_label(
            "DATA",
            position=(100, 100),
            rotation=0,
            shape="input"
        )

        hlabel_data = sch._data["hierarchical_labels"][0]
        assert hlabel_data["justify"] == "left"

    def test_hierarchical_label_justify_90deg(self):
        """Test justify is 'left' for 90° rotation."""
        sch = ksa.create_schematic("TestHLabelJustify")
        sch.add_hierarchical_label(
            "DATA",
            position=(100, 100),
            rotation=90,
            shape="input"
        )

        hlabel_data = sch._data["hierarchical_labels"][0]
        assert hlabel_data["justify"] == "left"

    def test_hierarchical_label_justify_180deg(self):
        """Test justify is 'right' for 180° rotation."""
        sch = ksa.create_schematic("TestHLabelJustify")
        sch.add_hierarchical_label(
            "DATA",
            position=(100, 100),
            rotation=180,
            shape="input"
        )

        hlabel_data = sch._data["hierarchical_labels"][0]
        assert hlabel_data["justify"] == "right"

    def test_hierarchical_label_justify_270deg(self):
        """Test justify is 'right' for 270° rotation."""
        sch = ksa.create_schematic("TestHLabelJustify")
        sch.add_hierarchical_label(
            "DATA",
            position=(100, 100),
            rotation=270,
            shape="input"
        )

        hlabel_data = sch._data["hierarchical_labels"][0]
        assert hlabel_data["justify"] == "right"


class TestGlobalLabelRotation:
    """Test rotation parameter support for global labels."""

    def test_global_label_with_rotation_0(self):
        """Test creating global label with 0° rotation."""
        sch = ksa.create_schematic("TestGlobalLabel")
        label_uuid = sch.add_global_label(
            "VCC",
            position=(100, 100),
            shape="input",
            rotation=0
        )

        # Find the global label in the data (stored as singular 'global_label')
        global_label = None
        for elem in sch._data.get("global_label", []):
            if elem.get("uuid") == label_uuid:
                global_label = elem
                break

        assert global_label is not None
        assert global_label["at"][2] == 0  # rotation is third element of 'at'

    def test_global_label_with_rotation_90(self):
        """Test creating global label with 90° rotation."""
        sch = ksa.create_schematic("TestGlobalLabel")
        label_uuid = sch.add_global_label(
            "VCC",
            position=(100, 100),
            shape="input",
            rotation=90
        )

        global_label = None
        for elem in sch._data.get("global_label", []):
            if elem.get("uuid") == label_uuid:
                global_label = elem
                break

        assert global_label is not None
        assert global_label["at"][2] == 90

    def test_global_label_with_rotation_180(self):
        """Test creating global label with 180° rotation."""
        sch = ksa.create_schematic("TestGlobalLabel")
        label_uuid = sch.add_global_label(
            "VCC",
            position=(100, 100),
            shape="input",
            rotation=180
        )

        global_label = None
        for elem in sch._data.get("global_label", []):
            if elem.get("uuid") == label_uuid:
                global_label = elem
                break

        assert global_label is not None
        assert global_label["at"][2] == 180

    def test_global_label_with_rotation_270(self):
        """Test creating global label with 270° rotation."""
        sch = ksa.create_schematic("TestGlobalLabel")
        label_uuid = sch.add_global_label(
            "VCC",
            position=(100, 100),
            shape="input",
            rotation=270
        )

        global_label = None
        for elem in sch._data.get("global_label", []):
            if elem.get("uuid") == label_uuid:
                global_label = elem
                break

        assert global_label is not None
        assert global_label["at"][2] == 270

    def test_global_label_rotation_persists_after_save_load(self):
        """Test that rotation persists through save/load cycle."""
        sch = ksa.create_schematic("TestGlobalLabel")
        sch.add_global_label(
            "GND",
            position=(100, 100),
            shape="input",
            rotation=270
        )

        # Save and reload
        sch.save("/tmp/test_global_label_rotation.kicad_sch")
        sch2 = ksa.Schematic.load("/tmp/test_global_label_rotation.kicad_sch")

        global_label = sch2._data.get("global_label", [])[0]
        assert global_label["at"][2] == 270


class TestGlobalLabelJustify:
    """Test automatic justify calculation for global labels."""

    def test_global_label_justify_0deg(self):
        """Test justify is 'left' for 0° rotation."""
        sch = ksa.create_schematic("TestGlobalLabelJustify")
        label_uuid = sch.add_global_label(
            "VCC",
            position=(100, 100),
            shape="input",
            rotation=0
        )

        global_label = None
        for elem in sch._data.get("global_label", []):
            if elem.get("uuid") == label_uuid:
                global_label = elem
                break

        effects = global_label.get("effects", {})
        justify = effects.get("justify", [])
        assert "left" in justify

    def test_global_label_justify_180deg(self):
        """Test justify is 'right' for 180° rotation."""
        sch = ksa.create_schematic("TestGlobalLabelJustify")
        label_uuid = sch.add_global_label(
            "VCC",
            position=(100, 100),
            shape="input",
            rotation=180
        )

        global_label = None
        for elem in sch._data.get("global_label", []):
            if elem.get("uuid") == label_uuid:
                global_label = elem
                break

        effects = global_label.get("effects", {})
        justify = effects.get("justify", [])
        assert "right" in justify

    def test_global_label_justify_270deg(self):
        """Test justify is 'right' for 270° rotation."""
        sch = ksa.create_schematic("TestGlobalLabelJustify")
        label_uuid = sch.add_global_label(
            "VCC",
            position=(100, 100),
            shape="input",
            rotation=270
        )

        global_label = None
        for elem in sch._data.get("global_label", []):
            if elem.get("uuid") == label_uuid:
                global_label = elem
                break

        effects = global_label.get("effects", {})
        justify = effects.get("justify", [])
        assert "right" in justify
