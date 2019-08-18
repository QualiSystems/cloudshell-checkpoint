#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import os

from cloudshell.devices.autoload.autoload_builder import AutoloadDetailsBuilder
from cloudshell.devices.standards.networking.autoload_structure import *

from cloudshell.checkpoint.gaia.autoload.snmp_if_table import SnmpIfTable


class CheckpointSNMPAutoload(object):

    def __init__(self, snmp_handler, shell_name, shell_type, resource_name, logger):
        """Basic init with injected snmp handler and logger

        :param snmp_handler:
        :param logger:
        :return:
        """

        self.snmp_handler = snmp_handler
        self.shell_name = shell_name
        self.shell_type = shell_type
        self.resource_name = resource_name
        self.logger = logger
        self.elements = {}
        self.resource = GenericResource(shell_name=shell_name,
                                        shell_type=shell_type,
                                        name=resource_name,
                                        unique_id=resource_name)

    def load_mibs(self):
        """
        Loads Checkpoint specific mibs inside snmp handler

        """
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mibs"))
        self.snmp_handler.update_mib_sources(path)

    def discover(self, supported_os):
        """General entry point for autoload,
        read device structure and attributes: chassis, modules, submodules, ports, port-channels and power supplies

        :return: AutoLoadDetails object
        """

        if not self._is_valid_device_os(supported_os):
            raise Exception(self.__class__.__name__, 'Unsupported device OS')

        self.logger.info("*" * 70)
        self.logger.info("Start SNMP discovery process .....")

        self.load_mibs()
        self.snmp_handler.load_mib(["CHECKPOINT-MIB"])
        self._get_device_details()

        chassis = self._get_chassis_attributes(self.resource)
        self._get_power_ports(chassis)
        self._get_ports_attributes(chassis)

        autoload_details = AutoloadDetailsBuilder(self.resource).autoload_details()
        self._log_autoload_details(autoload_details)
        return autoload_details

    def _log_autoload_details(self, autoload_details):
        """
        Logging autoload details
        :param autoload_details:
        :return:
        """
        self.logger.debug("-------------------- <RESOURCES> ----------------------")
        for resource in autoload_details.resources:
            self.logger.debug(
                "{0:15}, {1:20}, {2}".format(resource.relative_address, resource.name, resource.unique_identifier))
        self.logger.debug("-------------------- </RESOURCES> ----------------------")

        self.logger.debug("-------------------- <ATTRIBUTES> ---------------------")
        for attribute in autoload_details.attributes:
            self.logger.debug("-- {0:15}, {1:60}, {2}".format(attribute.relative_address, attribute.attribute_name,
                                                              attribute.attribute_value))
        self.logger.debug("-------------------- </ATTRIBUTES> ---------------------")

    def _is_valid_device_os(self, supported_os):
        """Validate device OS using snmp
            :return: True or False
        """

        system_description = self.snmp_handler.get_property('SNMPv2-MIB', 'sysObjectID', '0')
        self.logger.debug('Detected system description: \'{0}\''.format(system_description))
        result = re.search(r"({0})".format("|".join(supported_os)),
                           system_description,
                           flags=re.DOTALL | re.IGNORECASE)

        if result:
            return True
        else:
            error_message = 'Incompatible driver! Please use this driver for \'{0}\' operation system(s)'. \
                format(str(tuple(supported_os)))
            self.logger.error(error_message)
            return False

    def _get_ports_attributes(self, chassis):
        """Get resource details and attributes for every port in self.port_list

        :return:
        """

        self.logger.info("Load Ports:")
        SnmpIfTable.PORT_EXCLUDE_LIST.append("lo")
        if_table = SnmpIfTable(snmp_handler=self.snmp_handler, logger=self.logger)
        for port in if_table.if_ports:

            interface_name = port.if_name or port.if_descr_name
            if not interface_name:
                continue

            port_object = GenericPort(shell_name=self.shell_name,
                                      name=interface_name.replace("/", "-"),
                                      unique_id="{0}.{1}.{2}".format(self.resource_name, "port", port))

            port_object.port_description = port.if_port_description
            port_object.l2_protocol_type = port.if_type

            port_object.mac_address = port.if_mac
            port_object.mtu = port.if_mtu
            port_object.bandwidth = port.if_speed
            port_object.ipv4_address = port.ipv4_address
            port_object.ipv6_address = port.ipv6_address
            port_object.duplex = port.duplex
            port_object.auto_negotiation = port.auto_negotiation
            port_object.adjacent = port.adjacent

            chassis.add_sub_resource(port, port_object)

            self.logger.info("Added " + interface_name + " Port")

        self.logger.info("Building Ports completed")

    def _get_chassis_attributes(self, root_resource):
        """ Get Chassis element attributes """

        self.logger.info("Building Chassis")

        chassis_id = "0"
        serial_number = self.snmp_handler.get_property('CHECKPOINT-MIB',
                                                       "svnApplianceSerialNumber", chassis_id)
        chassis_object = GenericChassis(shell_name=self.shell_name,
                                        name="Chassis {}".format(chassis_id),
                                        unique_id="{}.{}.{}".format(self.resource_name, "chassis", serial_number))
        chassis_object.model = self.snmp_handler.get_property('CHECKPOINT-MIB', "svnApplianceProductName", chassis_id)
        chassis_object.serial_number = serial_number
        relative_address = "{0}".format(chassis_id)
        root_resource.add_sub_resource(relative_address, chassis_object)
        self.logger.info("Added " + chassis_object.model + " Chassis")
        self.logger.info("Building Chassis completed")

    def _get_device_details(self):
        """ Get root element attributes """

        self.logger.info("Building Root")
        self.resource.contact_name = self.snmp_handler.get_property('SNMPv2-MIB', 'sysContact', '0')
        self.resource.system_name = self.snmp_handler.get_property('SNMPv2-MIB', 'sysName', '0')
        self.resource.location = self.snmp_handler.get_property('SNMPv2-MIB', 'sysLocation', '0')
        self.resource.os_version = self.snmp_handler.get_property('CHECKPOINT-MIB', "svnVersion", '0')
        self.resource.vendor = self.snmp_handler.get_property('CHECKPOINT-MIB', "svnApplianceManufacturer", '0')
        self.resource.model = self.snmp_handler.get_property('CHECKPOINT-MIB', "svnApplianceProductName", '0')

    def _get_power_ports(self, chassis):
        """Get attributes for power ports provided in self.power_supply_list

        :return:
        """

        self.logger.info("Building PowerPorts")
        pp_table = self.snmp_handler.get_table("CHECKPOINT-MIB", "powerSupplyStatus")
        for port in pp_table:
            relative_address = "PP{}".format(port)

            power_port = GenericPowerPort(shell_name=self.shell_name,
                                          name="PP{0}".format(port),
                                          unique_id="{0}.{1}.{2}".format(self.resource_name, "power_port", port))
            status = pp_table.get(port, {}).get("powerSupplyStatus", "")
            if status:
                power_port.port_description = "Power port Status - " + status
            chassis.add_sub_resource(relative_address=relative_address, sub_resource=power_port)

            self.logger.info("Added Power Port")
        self.logger.info("Building Power Ports completed")


# if __name__ == "__main__":
#     from cloudshell.core.logger.qs_logger import get_qs_logger
#     from cloudshell.snmp.snmp_parameters import SNMPV2Parameters
#     from cloudshell.snmp.cloudshell_snmp import Snmp
#
#     logger = get_qs_logger()
#     # ip = "192.168.105.8"
#     # ip = "192.168.73.66"
#     ip = "192.168.73.102"
#     # ip = "192.168.105.11"
#     # ip = "192.168.105.4"
#     # ip = "192.168.73.142"
#     # ip = "192.168.42.235"
#     comm = "public"
#     # comm = "private"
#     # comm = "Aa123456"
#     # comm = "Cisco"
#     snmp_params = SNMPV2Parameters(ip, comm)
#     logger.info("started")
#     snmp_handler = Snmp(logger=logger, snmp_parameters=snmp_params)
#
#     with snmp_handler.get_snmp_service() as snmp_service:
#         snmp_service.update_mib_file_sources("D:\\_Quali_Git\\cloudshell-networking-cisco\\cloudshell\\networking\\cisco\\mibs")
#         if_table = SnmpIfTable(logger=logger, snmp_handler=snmp_service)
#
#         for port_id, port in if_table.if_ports.iteritems():
#             print port.ipv4_address
#             print port.ipv6_address
#
#         print("done")