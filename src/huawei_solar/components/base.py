"""The base every Huawei register component is built on."""

from __future__ import annotations

from typing import TYPE_CHECKING

from modbus_connection.model import Component

if TYPE_CHECKING:
    from collections.abc import Iterable

# Huawei inverters answer a read that spans at most 65 registers, and merging two
# runs of registers into one read only pays off while the unread gap between them
# stays under 16. Both limits come from the device, not from Modbus, so they are
# set once here rather than per component.
MAX_BATCHED_REGISTERS_SPAN = 65
MAX_BATCHED_REGISTERS_GAP = 15


class HuaweiComponent(Component):
    """A group of registers on a Huawei device, read in as few requests as it allows."""

    max_gap = MAX_BATCHED_REGISTERS_GAP
    max_span = MAX_BATCHED_REGISTERS_SPAN

    def restrict_fields(self, names: Iterable[str]) -> None:
        """Narrow this component to ``names``, without narrowing its readable map.

        ``restrict_fields`` marks the addresses of the fields it drops as
        unreadable, to keep a device's declared map honest. Huawei names three
        registers twice — 32066 is ``grid_voltage`` on a single-phase inverter
        and ``line_voltage_A_B`` on a three-phase one — so dropping one alias
        marks the address its twin still reads as unreadable, and the planner
        refuses a field that no readable range contains.

        No Huawei component declares readable ranges, so there is no device map
        to keep honest: clearing what narrowing synthesised leaves the plan
        covering exactly the fields that were kept.
        """
        super().restrict_fields(names)
        self.register_ranges = None
