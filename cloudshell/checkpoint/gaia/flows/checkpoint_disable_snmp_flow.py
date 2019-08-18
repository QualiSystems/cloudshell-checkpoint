#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.flows.cli_action_flows import DisableSnmpFlow
from cloudshell.snmp.snmp_parameters import SNMPV2Parameters


class CheckpointDisableSnmpFlow(DisableSnmpFlow):
    def __init__(self, cli_handler, logger):
        """
          Enable snmp flow
          :param cli_handler:
          :type cli_handler: JuniperCliHandler
          :param logger:
          :return:
          """
        super(CheckpointDisableSnmpFlow, self).__init__(cli_handler, logger)
        self._cli_handler = cli_handler

    def execute_flow(self, snmp_parameters=None):
        pass
