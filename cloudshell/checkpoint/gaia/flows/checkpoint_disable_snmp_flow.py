#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.flows.cli_action_flows import DisableSnmpFlow
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters

from cloudshell.checkpoint.gaia.command_actions.snmp_actions import SnmpV2Actions
from cloudshell.checkpoint.gaia.command_actions.snmp_actions import SnmpV3Actions


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

    def execute_flow(self, snmp_parameters):
        """

        :param cloudshell.snmp.snmp_parameters.SNMPParameters snmp_parameters:
        :return: commands output
        """
        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as cli_service:
            if isinstance(snmp_parameters, SNMPV3Parameters):
                disable_snmp = self._disable_snmp_v3
            else:
                disable_snmp = self._disable_snmp_v2

            disable_snmp(cli_service=cli_service, snmp_parameters=snmp_parameters)

    def _disable_snmp_v2(self, cli_service, snmp_parameters):
        """

        :param cloudshell.cli.cli_service_impl.CliServiceImpl cli_service:
        :param cloudshell.snmp.snmp_parameters.SNMPParameters snmp_parameters:
        :return: commands output
        """
        snmp_community = snmp_parameters.snmp_community

        if not snmp_community:
            raise Exception("SNMP community can not be empty")

        snmp_v2_actions = SnmpV2Actions(cli_service=cli_service, logger=self._logger)

        output = snmp_v2_actions.delete_snmp_community(snmp_community=snmp_community)
        output += snmp_v2_actions.disable_snmp_agent()

        return output

    def _disable_snmp_v3(self, cli_service, snmp_parameters):
        """

        :param cloudshell.cli.cli_service_impl.CliServiceImpl cli_service:
        :param cloudshell.snmp.snmp_parameters.SNMPParameters snmp_parameters:
        :return: commands output
        """
        snmp_v3_actions = SnmpV3Actions(cli_service, self._logger)

        output = snmp_v3_actions.delete_snmp_user(snmp_user=snmp_parameters.snmp_user)
        output += snmp_v3_actions.disable_snmp_agent()

        return output
