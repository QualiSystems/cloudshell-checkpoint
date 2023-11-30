from __future__ import annotations

import random
import re

from passlib.hash import md5_crypt
from typing import TYPE_CHECKING

from cloudshell.cli.service.command_mode import CommandMode

if TYPE_CHECKING:
    from logging import Logger

    from cloudshell.cli.service.cli_service import CliService
    from cloudshell.cli.service.auth_model import Auth


class MaintenanceCommandMode(CommandMode):
    PROMPT: str = r"(?:(?!\)).)#\s*$"  # TODO Verify prompt correctness
    ENTER_COMMAND: str = ""
    EXIT_COMMAND: str = ""

    def __init__(self, auth: Auth):
        """Initialize Maintenance Command Mode."""
        self._auth = auth
        CommandMode.__init__(
            self,
            MaintenanceCommandMode.PROMPT,
            MaintenanceCommandMode.ENTER_COMMAND,
            MaintenanceCommandMode.EXIT_COMMAND
        )


class EnableCommandMode(CommandMode):
    PROMPT: str = r">\s*$"
    ENTER_COMMAND: str = "clish"
    EXIT_COMMAND: str = ""

    def __init__(self, auth: Auth):
        """Initialize Enable Command Mode.

        Enable Command Mode - default command mode for CheckPoint Shells.
        """
        self._auth = auth
        CommandMode.__init__(
            self,
            EnableCommandMode.PROMPT,
            EnableCommandMode.ENTER_COMMAND,
            EnableCommandMode.EXIT_COMMAND
        )


class ExpertCommandMode(CommandMode):
    PROMPT: str = r"\[Expert.*#\s*$"
    ENTER_COMMAND: str = "expert"
    EXIT_COMMAND: str = "exit"

    def __init__(self, auth: Auth):
        """Initialize Expert Command Mode."""
        self._auth = auth
        CommandMode.__init__(
            self,
            ExpertCommandMode.PROMPT,
            ExpertCommandMode.ENTER_COMMAND,
            ExpertCommandMode.EXIT_COMMAND,
            enter_error_map={r"[Ww]rong\spassword": "Wrong password."},
            enter_action_map={
                r"[Ww]rong\spassword":
                    lambda s, l: self._exception("Incorrect Enable Password."),
                "[Pp]assword":
                    lambda session, logger: (
                        session.send_line(self._auth.enable_password, logger),
                        session.send_line("\n", logger),
                    )
            }
        )

    @staticmethod
    def _exception(message: str) -> None:
        raise Exception(message)

    @staticmethod
    def _expert_password_defined(cli_service: CliService, logger: Logger) -> bool:
        """Check if expert password defined."""
        logger.debug("Check if expert password defined.")
        if not isinstance(cli_service.command_mode, EnableCommandMode):
            raise Exception(
                "Cannot verify expert password, command mode is not correct"
            )
        else:
            result = cli_service.send_command("show configuration expert-password")
            return (
                re.match(r"^set\sexpert-password-hash\s.+$", result, re.MULTILINE)
                is not None
            )

    def _set_expert_password(self, cli_service: CliService, logger: Logger) -> None:
        """Set expert password."""
        # gen enable password hash
        enable_password_hash = md5_crypt.hash(
            self._auth.enable_password,
            salt_size=random.choice(range(5, 8))
        )

        error_map = {
            "Configuration lock present": "Configuration lock present.",
            "Failed to maintain the lock": "Failed to maintain the lock.",
            "Wrong password": "Wrong password."
        }
        cli_service.send_command(
            command=f"set expert-password-hash {enable_password_hash}",
            logger=logger,
            error_map=error_map,
        )

    def step_up(self, cli_service: CliService, logger: Logger) -> None:
        if not self._expert_password_defined(cli_service, logger):
            self._set_expert_password(cli_service, logger)
        super(ExpertCommandMode, self).step_up(cli_service, logger)


CommandMode.RELATIONS_DICT = {
    MaintenanceCommandMode: {
        EnableCommandMode: {
            ExpertCommandMode: {}
        }
    }
}
