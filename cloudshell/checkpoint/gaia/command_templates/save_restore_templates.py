from collections import OrderedDict

from cloudshell.cli.command_template.command_template import CommandTemplate

ERROR_MAP = OrderedDict([("Failed to maintain the lock", "Failed to maintain the lock."),
                         ("Incomplete command", "Incomplete command.")])
PASSWORD_ERROR_MAP = OrderedDict([
    ("must be at least", "Authentication pass phrase must be at least 8 characters"),
    ("not complex enough", "Password is not complex enough; try mixing more different kinds of characters "
                           "(upper case, lower case, digits, and punctuation)")])

LOCK_ACTION_MAP = OrderedDict([(r"Configuration lock present",
                                lambda s, l: s.send_line("lock database override", l))])

# Restore
ON_FAILURE_CONTINUE = CommandTemplate("set clienv on-failure continue", error_map=ERROR_MAP, action_map=LOCK_ACTION_MAP)
LOAD_CONFIGURATION = CommandTemplate("load configuration {filename}", error_map=ERROR_MAP, action_map=LOCK_ACTION_MAP)
ON_FAILURE_STOP = CommandTemplate("set clienv on-failure stop", error_map=ERROR_MAP, action_map=LOCK_ACTION_MAP)
SAVE_CONFIG = CommandTemplate("save config", error_map=ERROR_MAP, action_map=LOCK_ACTION_MAP)

# Save
SAVE_CONFIGURATION = CommandTemplate("save configuration {filename}",
                                     error_map=ERROR_MAP, action_map=LOCK_ACTION_MAP)

# RM file
REMOVE = CommandTemplate("rm {filename}")
