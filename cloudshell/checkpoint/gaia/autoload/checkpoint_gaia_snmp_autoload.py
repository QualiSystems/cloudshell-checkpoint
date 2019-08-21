#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import os

from cloudshell.devices.autoload.autoload_builder import AutoloadDetailsBuilder
from cloudshell.devices.standards.firewall.autoload_structure import *

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
        self._if_table = None

    @property
    def if_table(self):
        if not self._if_table:
            SnmpIfTable.PORT_EXCLUDE_LIST.extend(["lo", "sync"])
            self._if_table = SnmpIfTable(snmp_handler=self.snmp_handler, logger=self.logger)

        return self._if_table

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
        self.load_mibs()

        self.snmp_handler.load_mib(["CHECKPOINT-MIB"])
        if not self._is_valid_device_os(supported_os):
            raise Exception(self.__class__.__name__, 'Unsupported device OS')

        self.logger.info("*" * 70)
        self.logger.info("Start SNMP discovery process .....")


        self._get_device_details()

        chassis = self._get_chassis_attributes(self.resource)
        self._get_power_ports(chassis)
        self._get_ports_attributes(chassis)
        self._get_port_channels(self.resource)

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

        system_object_id = self.snmp_handler.get_property('SNMPv2-MIB', 'sysObjectID', '0')
        self.logger.debug('Detected system description: \'{0}\''.format(system_object_id))
        if any([x for x in supported_os if x in system_object_id.lower()]):
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

        for port in self.if_table.if_ports.values():

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

            chassis.add_sub_resource(port.if_index, port_object)

            self.logger.info("Added " + interface_name + " Port")

        self.logger.info("Building Ports completed")

    def _get_port_channels(self, root_resource):
        """Get all port channels and set attributes for them
        :return:
        """

        if not self.if_table.if_port_channels:
            return
        self.logger.info("Building Port Channels")
        for if_port_channel in self.if_table.if_port_channels.values():
            interface_model = if_port_channel.if_name
            match_object = re.search(r"\d+$", interface_model)
            if match_object:
                interface_id = "{0}".format(match_object.group(0))
                associated_ports = ""
                for port in if_port_channel.associated_port_list:
                    if_port_name = self.if_table.get_if_entity_by_index(port).if_name
                    associated_ports += if_port_name.replace('/', '-').replace(' ', '') + '; '

                port_channel = GenericPortChannel(shell_name=self.shell_name,
                                                  name=interface_model,
                                                  unique_id="{0}.{1}.{2}".format(self.resource_name,
                                                                                 "port_channel",
                                                                                 interface_id))

                port_channel.associated_ports = associated_ports.strip(' \t\n\r')
                port_channel.port_description = if_port_channel.if_port_description
                port_channel.ipv4_address = if_port_channel.ipv4_address
                port_channel.ipv6_address = if_port_channel.ipv6_address

                root_resource.add_sub_resource(interface_id, port_channel)

                self.logger.info("Added " + interface_model + " Port Channel")

            else:
                self.logger.error("Adding of {0} failed. Name is invalid".format(interface_model))

        self.logger.info("Building Port Channels completed")

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
        return chassis_object

    def _get_device_details(self):
        """ Get root element attributes """

        self.logger.info("Building Root")
        self.resource.contact_name = self.snmp_handler.get_property('SNMPv2-MIB', 'sysContact', '0')
        self.resource.system_name = self.snmp_handler.get_property('SNMPv2-MIB', 'sysName', '0')
        self.resource.location = self.snmp_handler.get_property('SNMPv2-MIB', 'sysLocation', '0')
        self.resource.os_version = self.snmp_handler.get_property('CHECKPOINT-MIB', "svnVersion", '0')
        self.resource.vendor = "Checkpoint"
        self.resource.model = self.snmp_handler.get_property('CHECKPOINT-MIB', "svnApplianceProductName", '0')

    def _get_power_ports(self, chassis):
        """Get attributes for power ports provided in self.power_supply_list

        :return:
        """

        self.logger.info("Building PowerPorts")
        pp_table = self.snmp_handler.get_table("CHECKPOINT-MIB", "powerSupplyTable")
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
