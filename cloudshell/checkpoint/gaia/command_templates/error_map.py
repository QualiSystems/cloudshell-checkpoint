from collections import OrderedDict

BASIC_ERRORS = OrderedDict(
    [
        ("[Cc]onfiguration lock present", "Configuration lock present"),
        ("Failed to maintain the lock", "Failed to maintain the lock."),
        ("Incomplete command", "Incomplete command."),
        ("No such file or directory", "No such file or directory"),
        ("[Ii]nvalid command", "Invalid command"),
    ]
)

PASSWORD_ERROR_MAP = OrderedDict(
    [
        (
            "must be at least",
            "Authentication pass phrase must be at least 8 characters",
        ),
        (
            "not complex enough",
            "Password is not complex enough; try mixing more different kinds "
            "of characters (upper case, lower case, digits, and punctuation)",
        ),
    ]
)
