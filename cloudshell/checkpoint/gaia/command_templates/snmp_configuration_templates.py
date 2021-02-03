from collections import OrderedDict

from cloudshell.cli.command_template.command_template import CommandTemplate

ERROR_MAP = OrderedDict([("[Cc]onfiguration lock present", "Configuration lock present")])
PASSWORD_ERROR_MAP = OrderedDict(list(ERROR_MAP.items()) + [
    ("must be at least", "Authentication pass phrase must be at least 8 characters"),
    ("not complex enough",
     "Password is not complex enough, try mixing more different kinds of characters "
     "(upper case, lower case, digits, and punctuation)")])

ENABLE_SNMP_AGENT = CommandTemplate("set snmp agent on", error_map=ERROR_MAP)
DISABLE_SNMP_AGENT = CommandTemplate("set snmp agent off", error_map=ERROR_MAP)
SET_SNMP_VERSION = CommandTemplate("set snmp agent-version {snmp_version}", error_map=ERROR_MAP)
SET_RO_SNMP_COMMUNITY = CommandTemplate("set snmp community {name} read-only", error_map=ERROR_MAP)
SET_RW_SNMP_COMMUNITY = CommandTemplate("set snmp community {name} read-write", error_map=ERROR_MAP)

SET_V3_SNMP_USER_NO_PRIV = CommandTemplate(
    "add snmp usm user {user} security-level authNoPriv auth-pass-phrase {password} "
    "authentication-protocol {auth_protocol}", error_map=PASSWORD_ERROR_MAP)

SET_V3_SNMP_USER_PRIV = CommandTemplate(
    "add snmp usm user {user} security-level authPriv auth-pass-phrase {password} "
    "authentication-protocol {auth_protocol} privacy-pass-phrase {private_key} "
    "privacy-protocol {priv_encrypt_protocol}", error_map=PASSWORD_ERROR_MAP)

SET_V3_SNMP_USER_RW = CommandTemplate("set snmp usm user {user} usm-read-write")

DELETE_SNMP_COMMUNITY = CommandTemplate("delete snmp community {name}", error_map=ERROR_MAP)
DELETE_V3_SNMP_USER = CommandTemplate("delete snmp usm user {user}", error_map=ERROR_MAP)
