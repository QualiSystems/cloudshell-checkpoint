from ipaddress import IPv4Address, IPv6Address

from cloudshell.checkpoint.gaia.autoload.port_constants import PORT_NAME, PORT_DESCR_NAME, PORT_DESCRIPTION
from cloudshell.snmp.core.domain.snmp_oid import SnmpMibObject


class SnmpIfEntity(object):
    def __init__(self, snmp_handler, logger, index, port_attributes_snmp_tables):
        self.if_index = index
        self._snmp = snmp_handler
        self._port_attributes_snmp_tables = port_attributes_snmp_tables
        self._logger = logger
        self._ipv4 = None
        self._ipv6 = None
        self._if_alias = None
        self._if_name = None
        self._if_descr_name = None
        self._ips_list = None

    @property
    def if_name(self):
        if not self._if_name:
            self._if_name = self._snmp.get_property(SnmpMibObject(*PORT_NAME + (self.if_index, ))).safe_value
        return self._if_name

    @property
    def if_descr_name(self):
        if not self._if_descr_name:
            self._if_descr_name = self._snmp.get_property(SnmpMibObject(*PORT_DESCR_NAME + (self.if_index, ))).safe_value
        return self._if_descr_name

    @property
    def if_port_description(self):
        if not self._if_alias:
            self._if_alias = self._snmp.get_property(SnmpMibObject(*PORT_DESCRIPTION + (self.if_index,))).safe_value
        return self._if_alias

    @property
    def ipv4_address(self):
        if not self._ipv4:
            if self._ips_list is None:
                self._get_ip()
            self._ipv4 = self._get_ipv4() or ""
        return self._ipv4

    @property
    def ipv6_address(self):
        if not self._ipv6:
            if self._ips_list is None:
                self._get_ip()
            self._ipv6 = self._get_ipv6() or ""
        return self._ipv6

    def _get_ip(self):
        self._ips_list = {x: y.get("ipAddressIfIndex").safe_value
                          for x, y in self._port_attributes_snmp_tables.ip_mixed_dict.items()
                          if y.get("ipAddressIfIndex").safe_value == self.if_index}
        for ip in self._ips_list:
            index = ip.replace("'", "")
            if index.startswith("ipv6"):
                try:
                    ipv6 = IPv6Address((index.replace("ipv6.0x", "")).decode("hex"))
                except:
                    ipv6 = ""
                self._ipv6 = ipv6
            elif index.startswith("ipv4"):
                try:
                    ipv4 = IPv4Address((index.replace("ipv4.0x", "")).decode("hex"))
                except:
                    ipv4 = ""
                self._ipv4 = ipv4

    def _get_ipv4(self):
        """Get IPv4 address details for provided port

        :return str IPv4 Address
        """

        if self._port_attributes_snmp_tables.ip_v4_old_dict:
            for snmp_response in self._port_attributes_snmp_tables.ip_v4_old_dict:
                response = self._port_attributes_snmp_tables.ip_v4_old_dict.get(snmp_response)
                if response and response == self.if_index:
                    return snmp_response

    def _get_ipv6(self):
        """Get IPv6 address details for provided port

        :return str IPv6 Address
        """

        if self._port_attributes_snmp_tables.ip_v6_dict:
            for snmp_response in self._port_attributes_snmp_tables.ip_v6_dict:
                response = self._port_attributes_snmp_tables.ip_v6_dict.get(snmp_response)

                if response and snmp_response.startswith("{}.".format(self.if_index)):
                    return snmp_response.replace("{}.".format(self.if_index), "")
