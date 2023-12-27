from __future__ import annotations

import logging
from collections.abc import Collection
from typing import TYPE_CHECKING, ClassVar

from attrs import define, field
from typing_extensions import Self

from cloudshell.cli.configurator import AbstractModeConfigurator
from cloudshell.cli.factory.session_factory import (
    CloudInfoAccessKeySessionFactory,
    ConsoleSessionFactory,
    GenericSessionFactory,
    SessionFactory,
)
from cloudshell.cli.service.command_mode_helper import CommandModeHelper
from cloudshell.cli.session.console_ssh import ConsoleSSHSession
from cloudshell.cli.session.console_telnet import ConsoleTelnetSession
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.telnet_session import TelnetSession

from cloudshell.checkpoint.cli.checkpoint_command_modes import (
    EnableCommandMode,
    ExpertCommandMode,
    MaintenanceCommandMode,
)

if TYPE_CHECKING:
    from cloudshell.cli.service.cli import CLI
    from cloudshell.cli.types import T_COMMAND_MODE_RELATIONS, CliConfigProtocol


@define
class CheckpointCliConfigurator(AbstractModeConfigurator):
    REGISTERED_SESSIONS: ClassVar[tuple[SessionFactory]] = (
        CloudInfoAccessKeySessionFactory(SSHSession),
        GenericSessionFactory(TelnetSession),
        ConsoleSessionFactory(ConsoleSSHSession),
        ConsoleSessionFactory(
            ConsoleTelnetSession, session_kwargs={"start_with_new_line": False}
        ),
        ConsoleSessionFactory(
            ConsoleTelnetSession, session_kwargs={"start_with_new_line": True}
        ),
    )
    modes: T_COMMAND_MODE_RELATIONS = field(init=False)

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        self.modes = CommandModeHelper.create_command_mode(self._auth)

    @classmethod
    def from_config(
        cls,
        conf: CliConfigProtocol,
        logger: logging.Logger | None = None,
        cli: CLI | None = None,
        registered_sessions: Collection[SessionFactory] | None = None,
    ) -> Self:
        if not logger:
            logger = logging.getLogger(__name__)
        return super().from_config(conf, logger, cli, registered_sessions)

    @property
    def default_mode(self):
        return self.modes[MaintenanceCommandMode]

    @property
    def enable_mode(self):
        return self.modes[EnableCommandMode]

    @property
    def config_mode(self):
        return self.modes[ExpertCommandMode]

    def _on_session_start(self, session, logger):
        """Send default commands to configure/clear session outputs."""
        session.send_line("set clienv rows 0", logger)
