#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

from cloudshell.shell.flows.autoload.basic_flow import AbstractAutoloadFlow

from cloudshell.checkpoint.gaia.autoload.checkpoint_gaia_snmp_autoload import (
    CheckpointSNMPAutoload,
)


class CheckpointSnmpAutoloadFlow(AbstractAutoloadFlow):
    def __init__(self, logger, snmp_configurator):
        super().__init__(logger)
        self._snmp_configurator = snmp_configurator

    def _autoload_flow(self, supported_os, resource_model):
        with self._snmp_configurator.get_service() as snmp_service:
            snmp_autoload = CheckpointSNMPAutoload(snmp_service, self._logger)
            if not self._is_valid_device_os(supported_os, snmp_autoload.device_info):
                raise Exception(self.__class__.__name__, "Unsupported device OS")

            snmp_autoload.load_mibs()

            snmp_autoload.build_root(resource_model)
            chassis_table = snmp_autoload.build_chassis(resource_model)
            snmp_autoload.build_power_modules(resource_model, chassis_table)
            snmp_autoload.build_ports(resource_model, chassis_table)
            snmp_autoload.build_port_channels(resource_model)
            autoload_details = resource_model.build()
        return autoload_details

    def _is_valid_device_os(self, supported_os, device_info):
        """Validate device OS using snmp.

        :return: True or False
        """
        self._logger.debug("Detected system description: '{0}'".format(device_info))
        result = re.search(
            r"({0})".format("|".join(supported_os)),
            device_info,
            flags=re.DOTALL | re.IGNORECASE,
        )

        if result:
            return True
        else:
            error_message = (
                "Incompatible driver! Please use this driver "
                "for '{0}' operation system(s)".format(str(tuple(supported_os)))
            )
            self._logger.error(error_message)
            return False

    def _log_device_details(self, autoload_details):
        """Logging autoload details.

        :param autoload_details:
        :return:
        """
        self._logger.debug("-------------------- <RESOURCES> ----------------------")
        for resource in autoload_details.resources:
            self._logger.debug(
                "{0:15}, {1:20}, {2}".format(
                    str(resource.relative_address),
                    resource.name,
                    resource.unique_identifier,
                )
            )
        self._logger.debug("-------------------- </RESOURCES> ----------------------")

        self._logger.debug("-------------------- <ATTRIBUTES> ---------------------")
        for attribute in autoload_details.attributes:
            self._logger.debug(
                "-- {0:15}, {1:60}, {2}".format(
                    str(attribute.relative_address),
                    attribute.attribute_name,
                    attribute.attribute_value,
                )
            )
        self._logger.debug("-------------------- </ATTRIBUTES> ---------------------")
