from collections import OrderedDict

from cloudshell.cli.command_template.command_template import CommandTemplate


PASSWORD_ERROR_MAP = OrderedDict([
    ("must be at least", "Authentication pass phrase must be at least 8 characters"),
    ("not complex enough", "Password is not complex enough; try mixing more different kinds of characters "
                           "(upper case, lower case, digits, and punctuation)")])

ENABLE_SNMP_AGENT = CommandTemplate("set snmp agent on")
DISABLE_SNMP_AGENT = CommandTemplate("set snmp agent off")
SET_SNMP_VERSION = CommandTemplate("set snmp agent-version {snmp_version}")
SET_RO_SNMP_COMMUNITY = CommandTemplate("set snmp community {name} read-only")
SET_RW_SNMP_COMMUNITY = CommandTemplate("set snmp community {name} read-write")

SET_V3_SNMP_USER_NO_PRIV = CommandTemplate(
    "add snmp usm user {user} security-level authNoPriv auth-pass-phrase {password} "
    "authentication-protocol {auth_protocol}", error_map=PASSWORD_ERROR_MAP)

SET_V3_SNMP_USER_PRIV = CommandTemplate(
    "add snmp usm user {user} security-level authPriv auth-pass-phrase {password} "
    "authentication-protocol {auth_protocol} privacy-pass-phrase {private_key} "
    "privacy-protocol {priv_encrypt_protocol}", error_map=PASSWORD_ERROR_MAP)

SET_V3_SNMP_USER_RW = CommandTemplate("set snmp usm user {user} usm-read-write")

DELETE_SNMP_COMMUNITY = CommandTemplate("delete snmp community {name}")
DELETE_V3_SNMP_USER = CommandTemplate("delete snmp usm user {user}")
