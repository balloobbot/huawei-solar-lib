"""The base every Huawei register component is built on."""

from __future__ import annotations

from modbus_connection.model import Component

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
