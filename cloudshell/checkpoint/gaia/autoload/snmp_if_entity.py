import binascii
import re
from collections import defaultdict
from functools import lru_cache
from ipaddress import IPv4Address, IPv6Address

from cloudshell.snmp.core.domain.snmp_oid import SnmpMibObject

from cloudshell.checkpoint.gaia.autoload.port_constants import (
    PORT_DESCR_NAME,
    PORT_DESCRIPTION,
    PORT_NAME,
)


class SnmpIfEntity(object):
    def __init__(self, snmp_handler, logger, index, port_attributes_snmp_tables):
        self.if_index = index
        self._snmp = snmp_handler
        self._port_attributes_snmp_tables = port_attributes_snmp_tables
        self._logger = logger
        self._if_alias = None
        self._if_name = None
        self._if_descr_name = None

    @property
    def if_name(self):
        if not self._if_name:
            self._if_name = self._snmp.get_property(
                SnmpMibObject(*PORT_NAME + (self.if_index,))
            ).safe_value
        return self._if_name

    @property
    def if_descr_name(self):
        if not self._if_descr_name:
            self._if_descr_name = self._snmp.get_property(
                SnmpMibObject(*PORT_DESCR_NAME + (self.if_index,))
            ).safe_value
        return self._if_descr_name

    @property
    def if_port_description(self):
        if not self._if_alias:
            self._if_alias = self._snmp.get_property(
                SnmpMibObject(*PORT_DESCRIPTION + (self.if_index,))
            ).safe_value
        return self._if_alias

    @property
    @lru_cache()
    def _ip_map(self):
        ip_map = defaultdict(list)
        for (
            ip_addr,
            index_obj,
        ) in self._port_attributes_snmp_tables.ip_mixed_dict.items():
            if str(index_obj.get("ipAddressIfIndex").safe_value) == str(self.if_index):
                ip_addr = ip_addr.strip("'")
                ip_map[ip_addr[:4]].append(ip_addr)
        return ip_map

    @property
    def ipv4_address(self):
        for ip_addr in self._ip_map.get("ipv4", []):
            try:
                return str(
                    IPv4Address(
                        binascii.unhexlify(re.sub(r"ipv4.*?\.0x", "", ip_addr))[:4]
                    )
                )
            except Exception:
                continue

        if self._port_attributes_snmp_tables.ip_v4_old_dict:
            for (
                ip_addr,
                index,
            ) in self._port_attributes_snmp_tables.ip_v4_old_dict.items():
                if str(index.get("ipAdEntIfIndex")) == str(self.if_index):
                    return ip_addr
        return ""

    @property
    def ipv6_address(self):
        for ip_addr in self._ip_map.get("ipv6", []):
            try:
                return str(
                    IPv6Address(
                        binascii.unhexlify(re.sub(r"ipv6.*?\.0x", "", ip_addr))[:16]
                    )
                )
            except Exception:
                continue

        if self._port_attributes_snmp_tables.ip_v6_dict:
            for snmp_response in self._port_attributes_snmp_tables.ip_v6_dict:
                response = self._port_attributes_snmp_tables.ip_v6_dict.get(
                    snmp_response
                )

                if response and snmp_response.startswith("{}.".format(self.if_index)):
                    return snmp_response.replace("{}.".format(self.if_index), "")

        return ""
