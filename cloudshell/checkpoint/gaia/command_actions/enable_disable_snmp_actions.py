from __future__ import annotations

from attrs import define
from typing import TYPE_CHECKING, ClassVar

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)
from cloudshell.checkpoint.gaia.command_templates import snmp_configuration_templates
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters

if TYPE_CHECKING:
    from cloudshell.cli.service.cli_service import CliService


@define
class BaseSnmpActions:
    _cli_service: CliService
    SNMP_AGENT_VERSION: ClassVar[str] = "any"

    def enable_snmp_agent(self, action_map: dict = None, error_map: dict = None) -> str:
        """Enable snmp."""
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=snmp_configuration_templates.ENABLE_SNMP_AGENT,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()

    def disable_snmp_agent(self, action_map: dict = None, error_map: dict = None) -> str:
        """Disable snmp."""
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=snmp_configuration_templates.DISABLE_SNMP_AGENT,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()

    def set_snmp_version(self, action_map: dict = None, error_map: dict = None) -> str:
        """Set SNMP version."""
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=snmp_configuration_templates.SET_SNMP_VERSION,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(snmp_version=self.SNMP_AGENT_VERSION)


class EnableDisableSnmpV2Actions(BaseSnmpActions):
    def set_snmp_read_community(self, snmp_community, action_map=None, error_map=None):
        """Set read community."""
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=snmp_configuration_templates.SET_RO_SNMP_COMMUNITY,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(name=snmp_community)

    def set_snmp_write_community(self, snmp_community, action_map=None, error_map=None):
        """Set write community."""
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=snmp_configuration_templates.SET_RW_SNMP_COMMUNITY,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(name=snmp_community)

    def delete_snmp_community(self, snmp_community, action_map=None, error_map=None):
        """Delete snmp community."""
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=snmp_configuration_templates.DELETE_SNMP_COMMUNITY,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(name=snmp_community)


class EnableDisableSnmpV3Actions(BaseSnmpActions):
    SNMP_AGENT_VERSION: ClassVar[str] = "v3-Only"

    AUTH_PROTOCOL_MAP = {
        SNMPV3Parameters.AUTH_MD5: "MD5",
        SNMPV3Parameters.AUTH_SHA: "SHA1",
    }

    PRIV_PROTOCOL_MAP = {
        SNMPV3Parameters.PRIV_NO_PRIV: "",
        SNMPV3Parameters.PRIV_DES: "DES",
        SNMPV3Parameters.PRIV_AES128: "AES",
    }

    def add_snmp_user(
        self,
        snmp_params: SNMPV3Parameters,
        action_map: dict = None,
        error_map: dict = None,
    ) -> str:
        """Add snmp user."""
        try:
            auth_protocol = self.AUTH_PROTOCOL_MAP[snmp_params.snmp_auth_protocol]
        except KeyError:
            raise Exception(
                f"Authentication protocol "
                f"{snmp_params.snmp_auth_protocol} is not supported.")

        try:
            priv_encrypt_protocol = self.PRIV_PROTOCOL_MAP[
                snmp_params.snmp_private_key_protocol
            ]
        except KeyError:
            raise Exception(
                f"Privacy Protocol "
                f"{snmp_params.snmp_private_key_protocol} is not supported."
            )

        if not priv_encrypt_protocol:
            return CommandTemplateExecutor(
                cli_service=self._cli_service,
                command_template=snmp_configuration_templates.SET_V3_SNMP_USER_NO_PRIV,
                action_map=action_map,
                error_map=error_map,
            ).execute_command(
                user=snmp_params.snmp_user,
                password=snmp_params.snmp_password,
                auth_protocol=auth_protocol,
            )

        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=snmp_configuration_templates.SET_V3_SNMP_USER_PRIV,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(
            user=snmp_params.snmp_user,
            password=snmp_params.snmp_password,
            auth_protocol=auth_protocol,
            private_key=snmp_params.snmp_private_key,
            priv_encrypt_protocol=priv_encrypt_protocol,
        )

    def delete_snmp_user(
        self,
        snmp_user: str,
        action_map: dict = None,
        error_map: dict = None,
    ) -> str:
        """Delete snmp user."""
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=snmp_configuration_templates.DELETE_V3_SNMP_USER,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(user=snmp_user)
