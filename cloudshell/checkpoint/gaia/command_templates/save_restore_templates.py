from collections import OrderedDict

from cloudshell.cli.command_template.command_template import CommandTemplate

PASSWORD_ERROR_MAP = OrderedDict([
    ("must be at least", "Authentication pass phrase must be at least 8 characters"),
    ("not complex enough", "Password is not complex enough; try mixing more different kinds of characters "
                           "(upper case, lower case, digits, and punctuation)")])

# Restore
ON_FAILURE_CONTINUE = CommandTemplate("set clienv on-failure continue")
LOAD_CONFIGURATION = CommandTemplate("load configuration {filename}")
ON_FAILURE_STOP = CommandTemplate("set clienv on-failure stop")
SAVE_CONFIG = CommandTemplate("save config")

# Save
SAVE_ERROR_MAP = OrderedDict([("Configuration lock present", "Configuration lock.")])
SAVE_CONFIGURATION = CommandTemplate("save configuration {filename}", error_map=SAVE_ERROR_MAP)

# SCP
SCP_ERROR_MAP = OrderedDict([("[Nn]o such file or directory", "No such file or directory.")])
SCP_ACTION_MAP = OrderedDict(
    [(r"\(yes\/no\)\?", lambda s, l: s.send_line("yes", l))])
SCP = CommandTemplate("scp {src_location} {dst_location}", action_map=SCP_ACTION_MAP, error_map=SCP_ERROR_MAP)

# RM file
REMOVE = CommandTemplate("rm {filename}")
