from __future__ import annotations

from cloudshell.snmp.autoload.services.port_table import PortsTable


class CheckpointPortsTable(PortsTable):
    PORT_EXCLUDE_LIST = PortsTable.PORT_EXCLUDE_LIST + ["lo", "sync", "loopback"]
    PORT_CHANNEL_NAME_LIST = PortsTable.PORT_CHANNEL_NAME_LIST + ["bond"]
