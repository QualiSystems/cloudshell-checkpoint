from cloudshell.snmp.snmp_configurator import EnableDisableSnmpFlowInterface

from cloudshell.checkpoint.gaia.command_actions.snmp_actions import (
    SnmpV2Actions,
    SnmpV3Actions,
)


class CheckpointEnableDisableSnmpFlow(EnableDisableSnmpFlowInterface):
    def __init__(self, cli_configurator, logger):
        """Enable Disable snmp flow.
        :param cloudshell.checkpoint.gaia.cli.checkpoint_cli_configurator.CheckpointCliConfigurator cli_configurator:  # noqa
        :param logging.Logger logger:
        :return:
        """
        self._cli_configurator = cli_configurator
        self._logger = logger

    def enable_snmp(self, snmp_parameters):
        with self._cli_configurator.enable_mode_service() as cli_service:
            if snmp_parameters.version == snmp_parameters.SnmpVersion.V3:
                enable_snmp_func = self._enable_snmp_v3
            else:
                enable_snmp_func = self._enable_snmp_v2

            enable_snmp_func(cli_service=cli_service, snmp_parameters=snmp_parameters)

    def disable_snmp(self, snmp_parameters):
        with self._cli_configurator.enable_mode_service() as cli_service:
            if snmp_parameters.version == snmp_parameters.SnmpVersion.V3:
                disable_snmp_func = self._disable_snmp_v3
            else:
                disable_snmp_func = self._disable_snmp_v2

            disable_snmp_func(cli_service=cli_service, snmp_parameters=snmp_parameters)

    def _enable_snmp_v2(self, cli_service, snmp_parameters):
        """Enable SNMPv2.

        :param cloudshell.cli.cli_service_impl.CliServiceImpl cli_service:
        :param cloudshell.snmp.snmp_parameters.SNMPReadParameters snmp_parameters:
        :return: commands output
        """
        snmp_community = snmp_parameters.snmp_community

        if not snmp_community:
            raise Exception("SNMP community can not be empty")

        snmp_v2_actions = SnmpV2Actions(cli_service=cli_service, logger=self._logger)
        output = snmp_v2_actions.enable_snmp_agent()
        output += snmp_v2_actions.set_snmp_version()

        if snmp_parameters.is_read_only:
            output += snmp_v2_actions.set_snmp_read_community(
                snmp_community=snmp_community
            )
        else:
            output += snmp_v2_actions.set_snmp_write_community(
                snmp_community=snmp_community
            )
        return output

    def _enable_snmp_v3(self, cli_service, snmp_parameters):
        """Enable SNMPv3.

        :param cloudshell.cli.cli_service_impl.CliServiceImpl cli_service:
        :param cloudshell.snmp.snmp_parameters.SNMPV3Parameters snmp_parameters:
        :return: commands output
        """
        snmp_v3_actions = SnmpV3Actions(cli_service=cli_service, logger=self._logger)
        output = snmp_v3_actions.enable_snmp_agent()
        output += snmp_v3_actions.set_snmp_version()

        output += snmp_v3_actions.add_snmp_user(
            snmp_user=snmp_parameters.snmp_user,
            snmp_password=snmp_parameters.snmp_password,
            snmp_priv_key=snmp_parameters.snmp_private_key,
            snmp_auth_proto=snmp_parameters.snmp_auth_protocol,
            snmp_priv_proto=snmp_parameters.snmp_private_key_protocol,
        )

        return output

    def _disable_snmp_v2(self, cli_service, snmp_parameters):
        """Disable SNMPv2.

        :param cloudshell.cli.cli_service_impl.CliServiceImpl cli_service:
        :param cloudshell.snmp.snmp_parameters.SNMPReadParameters snmp_parameters:
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
        """Disable SNMPv3.

        :param cloudshell.cli.cli_service_impl.CliServiceImpl cli_service:
        :param cloudshell.snmp.snmp_parameters.SNMPV3Parameters snmp_parameters:
        :return: commands output
        """
        snmp_v3_actions = SnmpV3Actions(cli_service, self._logger)

        output = snmp_v3_actions.delete_snmp_user(snmp_user=snmp_parameters.snmp_user)
        output += snmp_v3_actions.disable_snmp_agent()

        return output
