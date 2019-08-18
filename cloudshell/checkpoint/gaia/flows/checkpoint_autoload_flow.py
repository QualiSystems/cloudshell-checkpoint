#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.flows.snmp_action_flows import AutoloadFlow

from cloudshell.checkpoint.gaia.autoload.checkpoint_gaia_snmp_autoload import CheckpointSNMPAutoload


class CheckpointSnmpAutoloadFlow(AutoloadFlow):
    def execute_flow(self, supported_os, shell_name, shell_type, resource_name):
        with self._snmp_handler.get_snmp_service() as snmp_service:
            chekpoint_snmp_autoload = CheckpointSNMPAutoload(snmp_service,
                                                             shell_name,
                                                             shell_type,
                                                             resource_name,
                                                             self._logger)
            return chekpoint_snmp_autoload.discover(supported_os)
