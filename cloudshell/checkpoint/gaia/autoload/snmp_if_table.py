import re

from cloudshell.snmp.core.domain.snmp_oid import SnmpMibObject

from cloudshell.checkpoint.gaia.autoload import port_constants
from cloudshell.checkpoint.gaia.autoload.snmp_if_port_channel_entity import (
    SnmpIfPortChannel,
)
from cloudshell.checkpoint.gaia.autoload.snmp_if_port_entity import SnmpIfPort
from cloudshell.checkpoint.gaia.autoload.snmp_port_attr_tables import SnmpPortAttrTables


class SnmpIfTable(object):
    IF_PORT = SnmpIfPort
    IF_PORT_CHANNEL = SnmpIfPortChannel
    PORT_CHANNEL_NAME = "bond"
    PORT_EXCLUDE_LIST = ["mgmt", "management", "loopback", "null", "."]
    PORT_NAME_PATTERN = re.compile(r"((\d+/).+)")
    PORT_NAME_SECONDARY_PATTERN = re.compile(r"\d+")
    PORT_VALID_TYPE = re.compile(
        r"ethernet|other|propPointToPointSerial|fastEther|^otn", re.IGNORECASE
    )

    def __init__(self, snmp_handler, logger):
        self._snmp = snmp_handler
        self._logger = logger
        self._load_snmp_tables()
        self._if_entities_dict = {}
        self._if_port_dict = {}
        self._if_port_channels_dict = {}
        self._port_exclude_list = self.PORT_EXCLUDE_LIST
        self.port_attributes_snmp_tables = SnmpPortAttrTables(snmp_handler, logger)

    def set_port_exclude_list(self, value):
        if value:
            self._port_exclude_list = value

    def set_port_attributes_service(self, value):
        self.port_attributes_snmp_tables = value

    @property
    def if_ports(self):
        if not self._if_port_dict:
            self._get_if_entities()
        return self._if_port_dict

    @property
    def if_port_channels(self):
        if not self._if_port_channels_dict:
            self._get_port_channels()
        return self._if_port_channels_dict

    def get_if_entity_by_index(self, if_index):
        if not self._if_entities_dict:
            self._get_if_entities()
        return self.if_ports.get(if_index) or self.if_port_channels.get(if_index)

    def _get_if_entities(self):
        for port in self._if_table:
            port_obj = self.IF_PORT(
                snmp_handler=self._snmp,
                logger=self._logger,
                index=port,
                port_attributes_snmp_tables=self.port_attributes_snmp_tables,
            )
            if (
                any(
                    exclude_port
                    for exclude_port in self._port_exclude_list
                    if exclude_port in port_obj.if_descr_name.lower()
                    or exclude_port in port_obj.if_name.lower()
                )
                or port_obj.if_name.lower().startswith(self.PORT_CHANNEL_NAME)
                or port_obj.if_descr_name.lower().startswith(self.PORT_CHANNEL_NAME)
            ):
                continue
            self._if_port_dict[port] = port_obj

    def _get_port_channels(self):
        for port in self._if_table:
            if port in self._if_port_dict:
                continue
            port_channel_obj = self.IF_PORT_CHANNEL(
                snmp_handler=self._snmp,
                logger=self._logger,
                index=port,
                port_attributes_snmp_tables=self.port_attributes_snmp_tables,
            )
            if port_channel_obj.if_name.lower().startswith(
                self.PORT_CHANNEL_NAME
            ) or port_channel_obj.if_descr_name.lower().startswith(
                self.PORT_CHANNEL_NAME
            ):
                self._if_port_channels_dict[port] = port_channel_obj

    def _load_snmp_tables(self):
        """Load all cisco required snmp tables.

        :return:
        """
        self._logger.info("Start loading MIB tables:")
        if_table = self._snmp.get_table(SnmpMibObject(*port_constants.PORT_DESCR_NAME))
        if not if_table:
            if_table = self._snmp.get_table(SnmpMibObject(*port_constants.PORT_NAME))
            if not if_table:
                if_table = self._snmp.get_table(
                    SnmpMibObject(*port_constants.PORT_INDEX)
                )
        self._if_table = if_table.keys()
        self._logger.info("ifIndex table loaded")

    def get_if_index_from_port_name(self, port_name, port_filter_pattern):
        if_table_re = None
        port_if_match = self.PORT_NAME_PATTERN.search(port_name)
        if not port_if_match:
            port_if_re = self.PORT_NAME_SECONDARY_PATTERN.findall(port_name)
            if port_if_re:
                if_table_re = "/".join(port_if_re)
        else:
            port_if_re = port_if_match.group()
            if_table_re = port_if_re
        if if_table_re:
            for interface_id in self.if_ports:
                interface = self.if_ports.get(interface_id)
                if interface and not self.PORT_VALID_TYPE.search(interface.if_type):
                    continue
                if port_filter_pattern.search(str(interface.if_name)):
                    continue
                if (
                    port_name == interface.if_name
                    or port_name == interface.if_descr_name
                ):
                    return interface
                port_pattern = re.compile(
                    r"^\S*\D*{0}(/\D+|$)".format(if_table_re), re.IGNORECASE
                )
                if port_pattern.search(interface.if_name) or port_pattern.search(
                    interface.if_descr_name
                ):
                    return interface
