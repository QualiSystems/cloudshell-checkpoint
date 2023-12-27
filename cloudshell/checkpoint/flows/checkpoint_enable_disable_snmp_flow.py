from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define

from cloudshell.snmp.snmp_configurator import EnableDisableSnmpFlowInterface

from cloudshell.checkpoint.command_actions.enable_disable_snmp_actions import (  # noqa: E501
    EnableDisableSnmpV2Actions,
    EnableDisableSnmpV3Actions,
)
from cloudshell.checkpoint.helpers.errors import SnmpCheckpointError

if TYPE_CHECKING:
    from typing import Union

    from cloudshell.cli.service.cli_service import CliService
    from cloudshell.snmp.snmp_parameters import (
        SNMPReadParameters,
        SNMPV3Parameters,
        SNMPWriteParameters,
    )

    from ..cli.checkpoint_cli_configurator import CheckpointCliConfigurator

    SnmpParams = Union[SNMPReadParameters, SNMPWriteParameters, SNMPV3Parameters]


@define
class CheckpointEnableDisableSnmpFlow(EnableDisableSnmpFlowInterface):
    _cli_configurator: CheckpointCliConfigurator

    def enable_snmp(self, snmp_parameters: SnmpParams) -> None:
        with self._cli_configurator.enable_mode_service() as cli_service:
            if snmp_parameters.version == snmp_parameters.SnmpVersion.V3:
                self._enable_snmp_v3(cli_service, snmp_parameters)
            else:
                self._enable_snmp_v2(cli_service, snmp_parameters)

    def disable_snmp(self, snmp_parameters: SnmpParams) -> None:
        with self._cli_configurator.enable_mode_service() as cli_service:
            if snmp_parameters.version == snmp_parameters.SnmpVersion.V3:
                self._disable_snmp_v3(cli_service, snmp_parameters)
            else:
                self._disable_snmp_v2(cli_service, snmp_parameters)

    @staticmethod
    def _enable_snmp_v2(cli_service: CliService, snmp_parameters: SnmpParams) -> str:
        """Enable SNMPv2."""
        snmp_community = snmp_parameters.snmp_community

        if not snmp_community:
            raise SnmpCheckpointError("SNMP community can not be empty")

        snmp_v2_actions = EnableDisableSnmpV2Actions(cli_service=cli_service)
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

    @staticmethod
    def _enable_snmp_v3(cli_service: CliService, snmp_parameters: SnmpParams) -> str:
        """Enable SNMPv3."""
        snmp_v3_actions = EnableDisableSnmpV3Actions(cli_service=cli_service)
        output = snmp_v3_actions.enable_snmp_agent()
        output += snmp_v3_actions.set_snmp_version()
        output += snmp_v3_actions.add_snmp_user(snmp_params=snmp_parameters)

        return output

    @staticmethod
    def _disable_snmp_v2(cli_service: CliService, snmp_parameters: SnmpParams) -> str:
        """Disable SNMPv2."""
        snmp_community = snmp_parameters.snmp_community

        if not snmp_community:
            raise SnmpCheckpointError("SNMP community can not be empty")

        snmp_v2_actions = EnableDisableSnmpV2Actions(cli_service=cli_service)

        output = snmp_v2_actions.delete_snmp_community(snmp_community=snmp_community)
        output += snmp_v2_actions.disable_snmp_agent()

        return output

    @staticmethod
    def _disable_snmp_v3(cli_service: CliService, snmp_parameters: SnmpParams) -> str:
        """Disable SNMPv3."""
        snmp_v3_actions = EnableDisableSnmpV3Actions(cli_service)

        output = snmp_v3_actions.delete_snmp_user(snmp_user=snmp_parameters.snmp_user)
        output += snmp_v3_actions.disable_snmp_agent()

        return output
