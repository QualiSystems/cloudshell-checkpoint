#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.flows.cli_action_flows import EnableSnmpFlow
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters
from cloudshell.snmp.snmp_parameters import SNMPV2WriteParameters

from cloudshell.checkpoint.gaia.command_actions.snmp_actions import SnmpV2Actions
from cloudshell.checkpoint.gaia.command_actions.snmp_actions import SnmpV3Actions


class CheckpointEnableSnmpFlow(EnableSnmpFlow):
    def __init__(self, cli_handler, logger):
        """
        Enable snmp flow
        :param cli_handler:
        :param logger:
        :return:
        """
        super(CheckpointEnableSnmpFlow, self).__init__(cli_handler, logger)
        self._cli_handler = cli_handler

    def execute_flow(self, snmp_parameters):
        """

        :param cloudshell.snmp.snmp_parameters.SNMPParameters snmp_parameters:
        :return: commands output
        """
        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as cli_service:
            if isinstance(snmp_parameters, SNMPV3Parameters):
                enable_snmp = self._enable_snmp_v3
            else:
                enable_snmp = self._enable_snmp_v2

            enable_snmp(cli_service=cli_service, snmp_parameters=snmp_parameters)

    def _enable_snmp_v2(self, cli_service, snmp_parameters):
        """

        :param cloudshell.cli.cli_service_impl.CliServiceImpl cli_service:
        :param cloudshell.snmp.snmp_parameters.SNMPParameters snmp_parameters:
        :return: commands output
        """
        snmp_community = snmp_parameters.snmp_community

        if not snmp_community:
            raise Exception("SNMP community can not be empty")

        snmp_v2_actions = SnmpV2Actions(cli_service=cli_service, logger=self._logger)
        output = snmp_v2_actions.enable_snmp_agent()
        output += snmp_v2_actions.set_snmp_version()

        if isinstance(snmp_parameters, SNMPV2WriteParameters):
           output += snmp_v2_actions.set_snmp_write_community(snmp_community=snmp_community)
        else:
            output += snmp_v2_actions.set_snmp_read_community(snmp_community=snmp_community)

        return output

    def _enable_snmp_v3(self, cli_service, snmp_parameters):
        """

        :param cloudshell.cli.cli_service_impl.CliServiceImpl cli_service:
        :param cloudshell.snmp.snmp_parameters.SNMPParameters snmp_parameters:
        :return: commands output
        """
        snmp_v3_actions = SnmpV3Actions(cli_service=cli_service, logger=self._logger)
        output = snmp_v3_actions.enable_snmp_agent()
        output += snmp_v3_actions.set_snmp_version()

        output += snmp_v3_actions.add_snmp_user(snmp_user=snmp_parameters.snmp_user,
                                                snmp_password=snmp_parameters.snmp_password,
                                                snmp_priv_key=snmp_parameters.snmp_private_key,
                                                snmp_auth_proto=snmp_parameters.auth_protocol,
                                                snmp_priv_proto=snmp_parameters.private_key_protocol)

        return output
