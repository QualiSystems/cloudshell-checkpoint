from collections import OrderedDict

from cloudshell.cli.command_template.command_template import CommandTemplate

ERROR_MAP = OrderedDict([("Configuration lock present", "Configuration lock present."),
                         ("Failed to maintain the lock", "Failed to maintain the lock."),
                         ("Incomplete command", "Incomplete command.")])
PASSWORD_ERROR_MAP = OrderedDict([
    ("must be at least", "Authentication pass phrase must be at least 8 characters"),
    ("not complex enough", "Password is not complex enough; try mixing more different kinds of characters "
                           "(upper case, lower case, digits, and punctuation)")])

# Restore
ON_FAILURE_CONTINUE = CommandTemplate("set clienv on-failure continue", error_map=ERROR_MAP)
LOAD_CONFIGURATION = CommandTemplate("load configuration {filename}", error_map=ERROR_MAP)
ON_FAILURE_STOP = CommandTemplate("set clienv on-failure stop", error_map=ERROR_MAP)
SAVE_CONFIG = CommandTemplate("save config", error_map=ERROR_MAP)

# Save
SAVE_CONFIGURATION = CommandTemplate("save configuration {filename}", error_map=ERROR_MAP)

# RM file
REMOVE = CommandTemplate("rm {filename}")
