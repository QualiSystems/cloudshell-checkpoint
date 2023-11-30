from __future__ import annotations

from cloudshell.cli.command_template.command_template import CommandTemplate

from cloudshell.checkpoint.gaia.command_templates.error_map import (
    BASIC_ERRORS,
    PASSWORD_ERROR_MAP,
)

SNMP_ERROR_MAP = {
    "does not accept community strings": "SNMP v3-Only does not accept community strings."  # noqa E501
}

ERROR_MAP = BASIC_ERRORS | SNMP_ERROR_MAP
SNMP_PASSWORD_ERROR_MAP = BASIC_ERRORS | PASSWORD_ERROR_MAP


ENABLE_SNMP_AGENT = CommandTemplate("set snmp agent on", error_map=ERROR_MAP)
DISABLE_SNMP_AGENT = CommandTemplate("set snmp agent off", error_map=ERROR_MAP)
SET_SNMP_VERSION = CommandTemplate(
    "set snmp agent-version {snmp_version}", error_map=ERROR_MAP
)
SET_RO_SNMP_COMMUNITY = CommandTemplate(
    "set snmp community {name} read-only", error_map=ERROR_MAP
)
SET_RW_SNMP_COMMUNITY = CommandTemplate(
    "set snmp community {name} read-write", error_map=ERROR_MAP
)

SET_V3_SNMP_USER_NO_PRIV = CommandTemplate(
    "add snmp usm user {user} security-level authNoPriv auth-pass-phrase {password} "
    "authentication-protocol {auth_protocol}",
    error_map=SNMP_PASSWORD_ERROR_MAP,
)

SET_V3_SNMP_USER_PRIV = CommandTemplate(
    "add snmp usm user {user} security-level authPriv auth-pass-phrase {password} "
    "authentication-protocol {auth_protocol} privacy-pass-phrase {private_key} "
    "privacy-protocol {priv_encrypt_protocol}",
    error_map=SNMP_PASSWORD_ERROR_MAP,
)

SET_V3_SNMP_USER_RW = CommandTemplate("set snmp usm user {user} usm-read-write")

DELETE_SNMP_COMMUNITY = CommandTemplate(
    "delete snmp community {name}", error_map=ERROR_MAP
)
DELETE_V3_SNMP_USER = CommandTemplate(
    "delete snmp usm user {user}", error_map=ERROR_MAP
)
