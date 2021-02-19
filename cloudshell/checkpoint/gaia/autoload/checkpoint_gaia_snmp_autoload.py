#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re

from cloudshell.snmp.core.domain.snmp_oid import SnmpMibObject

from cloudshell.checkpoint.gaia.autoload.snmp_if_table import SnmpIfTable


class CheckpointSNMPAutoload(object):
    CHASSIS_ID = "0"

    def __init__(self, snmp_service, logger):
        """Basic init with injected snmp handler and logger.

        :param snmp_service:
        :param logger:
        :return:
        """
        self.snmp_service = snmp_service
        self.logger = logger

        self._if_table = None

    @property
    def if_table(self):
        if not self._if_table:
            SnmpIfTable.PORT_EXCLUDE_LIST.extend(["lo", "sync"])
            self._if_table = SnmpIfTable(
                snmp_handler=self.snmp_service, logger=self.logger
            )

        return self._if_table

    def load_mibs(self):
        """Loads Checkpoint specific mibs inside snmp handler."""
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mibs"))
        self.snmp_service.add_mib_folder_path(path)
        self.logger.info("Loading mibs")
        self.snmp_service.load_mib_tables(["CHECKPOINT-MIB"])

    @property
    def device_info(self):
        system_description = self.snmp_service.get_property(
            SnmpMibObject("SNMPv2-MIB", "sysObjectID", "0")
        ).safe_value
        return system_description

    def build_ports(self, resource_model, chassis_table):
        """Get resource details and attributes for every port in self.port_list.

        :param cloudshell.shell.standards.firewall.autoload_model.
        FirewallResourceModel resource_model:
        :param dict chassis_table:
        """
        self.logger.info("Load Ports:")
        chassis = chassis_table.get(self.CHASSIS_ID)

        for port in self.if_table.if_ports.values():

            interface_name = port.if_name or port.if_descr_name
            if not interface_name:
                continue

            port_object = resource_model.entities.Port(
                port.if_index, name=interface_name
            )

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

            chassis.connect_port(port_object)

            self.logger.info("Added " + interface_name + " Port")

        self.logger.info("Building Ports completed")

    def build_port_channels(self, resource_model):
        """Get all port channels and set attributes for them.

        :param cloudshell.shell.standards.firewall.autoload_model.
        FirewallResourceModel resource_model:
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
                    associated_ports += (
                        if_port_name.replace("/", "-").replace(" ", "") + "; "
                    )

                port_channel = resource_model.entities.PortChannel(
                    interface_id, name=if_port_channel.if_name
                )
                port_channel.associated_ports = associated_ports.strip(" \t\n\r")
                port_channel.port_description = if_port_channel.if_port_description
                port_channel.ipv4_address = if_port_channel.ipv4_address
                port_channel.ipv6_address = if_port_channel.ipv6_address

                resource_model.connect_port_channel(port_channel)

                self.logger.info("Added " + interface_model + " Port Channel")

            else:
                self.logger.error(
                    "Adding of {0} failed. Name is invalid".format(interface_model)
                )

        self.logger.info("Building Port Channels completed")

    def build_chassis(self, resource_model):
        """Get Chassis element attributes.

        :param cloudshell.shell.standards.firewall.autoload_model.
        FirewallResourceModel resource_model:
        """
        self.logger.info("Building Chassis")

        chassis_id = self.CHASSIS_ID
        serial_number = self.snmp_service.get_property(
            SnmpMibObject("CHECKPOINT-MIB", "svnApplianceSerialNumber", chassis_id)
        ).safe_value
        chassis_object = resource_model.entities.Chassis(chassis_id)
        chassis_object.model = self.snmp_service.get_property(
            SnmpMibObject("CHECKPOINT-MIB", "svnApplianceProductName", chassis_id)
        ).safe_value
        chassis_object.serial_number = serial_number
        resource_model.connect_chassis(chassis_object)
        self.logger.info("Added " + chassis_object.model + " Chassis")
        self.logger.info("Building Chassis completed")
        return {chassis_id: chassis_object}

    def build_root(self, resource_model):
        """Get root element attributes.

        :param cloudshell.shell.standards.firewall.autoload_model.
        FirewallResourceModel resource_model:
        """
        self.logger.info("Building Root")
        resource_model.contact_name = self.snmp_service.get_property(
            SnmpMibObject("SNMPv2-MIB", "sysContact", "0")
        ).safe_value
        resource_model.system_name = self.snmp_service.get_property(
            SnmpMibObject("SNMPv2-MIB", "sysName", "0")
        ).safe_value
        resource_model.location = self.snmp_service.get_property(
            SnmpMibObject("SNMPv2-MIB", "sysLocation", "0")
        ).safe_value
        resource_model.os_version = self.snmp_service.get_property(
            SnmpMibObject("CHECKPOINT-MIB", "svnVersion", "0")
        ).safe_value
        resource_model.vendor = "Checkpoint"
        resource_model.model = self.snmp_service.get_property(
            SnmpMibObject("CHECKPOINT-MIB", "svnApplianceProductName", "0")
        ).safe_value

    def build_power_modules(self, resource_model, chassis_table):
        """Get attributes for power ports provided in self.power_supply_list.

        :param cloudshell.shell.standards.firewall.autoload_model.
        FirewallResourceModel resource_model:
        :param dict chassis_table:
        """
        power_port_table = {}
        self.logger.info("Building PowerPorts")
        pp_table = self.snmp_service.get_table(
            SnmpMibObject("CHECKPOINT-MIB", "powerSupplyTable")
        )
        chassis = chassis_table.get(self.CHASSIS_ID)
        for port_id in pp_table:
            power_port = resource_model.entities.PowerPort(port_id)

            status = pp_table.get(port_id, {}).get("powerSupplyStatus", "")
            if status:
                power_port.port_description = "Power port Status - " + status
            chassis.connect_power_port(power_port)
            power_port_table[port_id] = power_port
            self.logger.info("Added Power Port")
        self.logger.info("Building Power Ports completed")
        return power_port_table
