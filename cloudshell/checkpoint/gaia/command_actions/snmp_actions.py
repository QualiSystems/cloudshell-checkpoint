#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters

from cloudshell.checkpoint.gaia.command_templates import (
    snmp_configuration_templates as enable_disable_snmp,
)


class BaseSnmpActions(object):
    SNMP_AGENT_VERSION = "any"

    def __init__(self, cli_service, logger):
        """Snmp actions.

        :param cli_service: config mode cli service
        :type cli_service: CliService
        :param logger:
        :type logger: Logger
        :return:
        """
        self._cli_service = cli_service
        self._logger = logger

    def enable_snmp_agent(self, action_map=None, error_map=None):
        """Enable snmp.

        :param action_map:
        :param error_map:
        :return:
        """
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=enable_disable_snmp.ENABLE_SNMP_AGENT,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()

    def disable_snmp_agent(self, action_map=None, error_map=None):
        """Disable snmp.

        :param action_map:
        :param error_map:
        :return:
        """
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=enable_disable_snmp.DISABLE_SNMP_AGENT,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()

    def set_snmp_version(self, action_map=None, error_map=None):
        """Set version.

        :param action_map:
        :param error_map:
        :return:
        """
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=enable_disable_snmp.SET_SNMP_VERSION,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(snmp_version=self.SNMP_AGENT_VERSION)


class SnmpV2Actions(BaseSnmpActions):
    def set_snmp_read_community(self, snmp_community, action_map=None, error_map=None):
        """Set read community.

        :param snmp_community:
        :param action_map:
        :param error_map:
        :return:
        """
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=enable_disable_snmp.SET_RO_SNMP_COMMUNITY,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(name=snmp_community)

    def set_snmp_write_community(self, snmp_community, action_map=None, error_map=None):
        """Set write community.

        :param snmp_community:
        :param action_map:
        :param error_map:
        :return:
        """
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=enable_disable_snmp.SET_RW_SNMP_COMMUNITY,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(name=snmp_community)

    def delete_snmp_community(self, snmp_community, action_map=None, error_map=None):
        """Delete snmp community.

        :param snmp_community:
        :param action_map:
        :param error_map:
        :return:
        """
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=enable_disable_snmp.DELETE_SNMP_COMMUNITY,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(name=snmp_community)


class SnmpV3Actions(BaseSnmpActions):
    SNMP_AGENT_VERSION = "v3-Only"

    AUTH_COMMAND_MAP = {
        SNMPV3Parameters.AUTH_MD5: "MD5",
        SNMPV3Parameters.AUTH_SHA: "SHA1",
    }

    PRIV_COMMAND_MAP = {
        SNMPV3Parameters.PRIV_NO_PRIV: "",
        SNMPV3Parameters.PRIV_DES: "DES",
        SNMPV3Parameters.PRIV_AES128: "AES",
    }

    def add_snmp_user(
        self,
        snmp_user,
        snmp_password,
        snmp_priv_key,
        snmp_auth_proto,
        snmp_priv_proto,
        action_map=None,
        error_map=None,
    ):
        """Add snmp user.

        :param snmp_user:
        :param snmp_password:
        :param snmp_priv_key:
        :param snmp_auth_proto:
        :param snmp_priv_proto:
        :param action_map:
        :param error_map:
        :return:
        """
        try:
            auth_command_template = self.AUTH_COMMAND_MAP[snmp_auth_proto]
        except KeyError:
            raise Exception(
                "Authentication protocol {} is not supported".format(snmp_auth_proto)
            )

        try:
            priv_command_template = self.PRIV_COMMAND_MAP[snmp_priv_proto]
        except KeyError:
            raise Exception(
                "Privacy Protocol {} is not supported".format(snmp_priv_proto)
            )

        if not priv_command_template:
            return CommandTemplateExecutor(
                cli_service=self._cli_service,
                command_template=enable_disable_snmp.SET_V3_SNMP_USER_NO_PRIV,
                action_map=action_map,
                error_map=error_map,
            ).execute_command(
                user=snmp_user,
                password=snmp_password,
                auth_protocol=auth_command_template,
            )

        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=enable_disable_snmp.SET_V3_SNMP_USER_PRIV,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(
            user=snmp_user,
            password=snmp_password,
            auth_protocol=auth_command_template,
            private_key=snmp_priv_key,
            priv_encrypt_protocol=priv_command_template,
        )

    def delete_snmp_user(self, snmp_user, action_map=None, error_map=None):
        """Delete snmp user.

        :param snmp_user:
        :param action_map:
        :param error_map:
        :return:
        """
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=enable_disable_snmp.DELETE_V3_SNMP_USER,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(user=snmp_user)
