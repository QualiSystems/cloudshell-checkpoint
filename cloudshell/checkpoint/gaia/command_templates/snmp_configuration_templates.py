from cloudshell.cli.command_template.command_template import CommandTemplate

ENABLE_SNMP = CommandTemplate("set snmp agent on")
DISABLE_SNMP = CommandTemplate("set snmp agent off")
SET_SNMP_VERSION = CommandTemplate("set snmp agent-version {snmp_version}")
SET_RO_SNMP_COMMUNITY = CommandTemplate("set snmp community {name} read-only")
SET_RW_SNMP_COMMUNITY = CommandTemplate("set snmp community {name} read-write")
SET_V3_SNMP_USER = CommandTemplate("add snmp usm user {user} security-level authPriv auth-pass-phrase {password} "
                                   "privacy-pass-phrase {private_key} privacy-protocol {priv_encrypt_protocol}")
SET_V3_SNMP_USER_RW = CommandTemplate("set snmp usm user {user} usm-read-write")
