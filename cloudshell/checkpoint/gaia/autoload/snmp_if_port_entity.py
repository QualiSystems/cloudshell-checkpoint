import re

from cloudshell.snmp.core.domain.snmp_oid import SnmpMibObject

from cloudshell.checkpoint.gaia.autoload import port_constants
from cloudshell.checkpoint.gaia.autoload.snmp_if_entity import SnmpIfEntity


class SnmpIfPort(SnmpIfEntity):
    IF_TYPE_REPLACE_PATTERN = re.compile("^[/']|[/']$")
    ADJACENT_TEMPLATE = "{remote_host} through {remote_port}"

    def __init__(self, snmp_handler, logger, index, port_attributes_snmp_tables):
        super(SnmpIfPort, self).__init__(
            snmp_handler, logger, index, port_attributes_snmp_tables
        )
        self._snmp = snmp_handler
        self._port_attributes_snmp_tables = port_attributes_snmp_tables
        self._logger = logger
        self._if_type = None
        self._if_speed = None
        self._if_mtu = None
        self._if_mac = None
        self._adjacent = None
        self._duplex = None
        self._auto_neg = None

    @property
    def if_type(self):
        if not self._if_type:
            self._if_type = "other"
            if_type = self._snmp.get_property(
                SnmpMibObject(*(port_constants.PORT_TYPE + (self.if_index,)))
            ).safe_value
            if if_type and if_type:
                self._if_type = if_type.replace("'", "")
        return self._if_type

    @property
    def if_speed(self):
        if not self._if_speed:
            self._if_speed = self._snmp.get_property(
                SnmpMibObject(*(port_constants.PORT_SPEED + (self.if_index,)))
            ).safe_value
        return self._if_speed

    @property
    def if_mtu(self):
        if not self._if_mtu:
            self._if_mtu = self._snmp.get_property(
                SnmpMibObject(*(port_constants.PORT_MTU + (self.if_index,)))
            ).safe_value
        return self._if_mtu

    @property
    def if_mac(self):
        if not self._if_mac:
            self._if_mac = self._snmp.get_property(
                SnmpMibObject(*(port_constants.PORT_MAC + (self.if_index,)))
            ).safe_value
        return self._if_mac

    @property
    def adjacent(self):
        if not self._adjacent:
            self._adjacent = self._get_adjacent() or ""
        return self._adjacent

    @property
    def duplex(self):
        if not self._duplex:
            self._duplex = self._get_duplex() or "Half"
        return self._duplex

    @property
    def auto_negotiation(self):
        if not self._auto_neg:
            self._auto_neg = self._get_auto_neg() or "False"
        return self._auto_neg

    def _get_adjacent(self):
        """Get ajacent.

        Get connected device interface and device name to the specified
        port id, using cdp or lldp protocols.

        :return: device's name and port connected to port id
        :rtype string
        """
        # ToDo rebuild this. Iterating through dictionary
        #  again and again looks bad, very bad.
        if self._port_attributes_snmp_tables.lldp_local_table:
            if_name = self.if_name
            if not if_name:
                if_name = ""
            interface_name = if_name.lower()
            if interface_name:
                key = self._port_attributes_snmp_tables.lldp_local_table.get(
                    interface_name, None
                )
                if key:
                    for (
                        port_id,
                        rem_table,
                    ) in self._port_attributes_snmp_tables.lldp_remote_table.items():
                        if key in port_id.split("."):
                            remote_sys_name = rem_table.get("lldpRemSysName")
                            remote_port_name = self._snmp.get_property(
                                SnmpMibObject(
                                    **(
                                        port_constants.PORT_ADJACENT_REM_PORT_DESCR
                                        + (port_id,)
                                    )
                                )
                            ).safe_value
                            if remote_port_name and remote_sys_name:
                                return self.ADJACENT_TEMPLATE.format(
                                    remote_host=remote_sys_name,
                                    remote_port=remote_port_name,
                                )

    def _get_auto_neg(self):
        """Get port auto negotiation status.

        :return return "True"
        """
        index = "{}.{}".format(self.if_index, 1)
        auto_negotiation = self._snmp.get_property(
            SnmpMibObject(*(port_constants.PORT_AUTO_NEG + (index,)))
        ).safe_value
        if auto_negotiation and "enabled" in auto_negotiation.lower():
            return "True"

    def _get_duplex(self):
        """Get current duplex state.

        :return str "Full"
        """
        for key, value in self._port_attributes_snmp_tables.duplex_table.items():
            if "dot3StatsIndex" in value.keys() and value["dot3StatsIndex"] == str(
                self.if_index
            ):
                interface_duplex = self._snmp.get_property(
                    SnmpMibObject("EtherLike-MIB", "dot3StatsDuplexStatus", key)
                ).safe_value
                if "fullDuplex" in interface_duplex:
                    return "Full"
