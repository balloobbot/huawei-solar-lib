"""Check the component register map against what the old table used to decode.

The map was moved from a single 744-entry table of ``RegisterDefinition``
objects onto ``modbus_connection`` components. None of it can be checked against
real hardware, so ``legacy_decode_vectors.json`` freezes what the old decoders
returned for a set of word patterns per register — including the all-ones
pattern that trips each register's "value not available" sentinel — and these
tests replay them through the new fields.

Regenerating the fixture is not a way to make a failure go away: it is the
record of the behaviour the migration promised to preserve.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest
from huawei_solar.registry import REGISTER_LOCATIONS, RegisterLocation

from huawei_solar import register_values as rv

VECTORS = json.loads((Path(__file__).parent.parent / "fixtures" / "legacy_decode_vectors.json").read_text())


def canonical(value: Any) -> str:
    """Render a decoded value the same way the fixture was rendered."""
    rendered = repr(value)
    return re.sub(r"<ChargeFlag\.(\w+): \d+>", r"ChargeFlag.\1", rendered)


def effective_address(location: RegisterLocation) -> int:
    """Resolve the address this location reads, taking its instance index into account."""
    field = location.definition
    if location.index is None:
        return field.address
    return field.address + field.stride * (location.index - 1)


def test_every_register_has_a_location() -> None:
    """No register was dropped on the way into the component model."""
    assert set(REGISTER_LOCATIONS) == set(VECTORS)


def test_no_component_field_is_unreachable() -> None:
    """Every declared field is reachable under a published register name."""
    declared = {(location.component, location.field) for location in REGISTER_LOCATIONS.values()}
    components = {location.component for location in REGISTER_LOCATIONS.values()}
    orphans = {
        (component.__name__, name)
        for component in components
        for name in component.declared_fields
        if (component, name) not in declared
    }
    assert not orphans


@pytest.mark.parametrize("name", sorted(VECTORS))
def test_register_layout_matches_legacy_table(name: str) -> None:
    """Address, width and writability survived the move."""
    expected = VECTORS[name]
    location = REGISTER_LOCATIONS[name]
    field = location.definition

    assert effective_address(location) == expected["address"], "address moved"
    assert field.count == expected["count"], "register width changed"
    assert bool(field.writable) == expected["writable"], "writability changed"


ENCODABLE = sorted(name for name, entry in VECTORS.items() if "encode_vectors" in entry)

# A write too large for its register used to escape as a bare ``struct.error``
# from packing the register's struct format. It is rejected just as firmly now,
# but as the library's own typed exception.
EQUIVALENT_ERRORS = {"ERR:error": "ERR:WriteException"}


@pytest.mark.parametrize("name", ENCODABLE)
def test_register_encodes_as_it_used_to(name: str) -> None:
    """Each writable register encodes to the same words it always did.

    The values are rendered with ``repr`` in the fixture, so they are evaluated
    back with the register-value enums in scope.
    """
    field = REGISTER_LOCATIONS[name].definition
    for rendered, expected in VECTORS[name]["encode_vectors"]:
        value = eval(rendered, {"rv": rv, **vars(rv)})  # noqa: S307
        try:
            actual: Any = field.encode(value)
        except Exception as err:  # noqa: BLE001
            actual = f"ERR:{type(err).__name__}"
        wanted = EQUIVALENT_ERRORS.get(expected, expected) if isinstance(expected, str) else expected
        assert actual == wanted, f"{name} encoding {rendered}"


@pytest.mark.parametrize("name", sorted(VECTORS))
def test_register_decodes_as_it_used_to(name: str) -> None:
    """Each register decodes every frozen word pattern to the same value."""
    location = REGISTER_LOCATIONS[name]
    field = location.definition

    for words, expected in VECTORS[name]["vectors"]:
        try:
            actual = canonical(field.decode(list(words)))
        except Exception as err:  # noqa: BLE001
            actual = f"ERR:{type(err).__name__}"
        assert actual == expected, f"{name} decoding {words}"
