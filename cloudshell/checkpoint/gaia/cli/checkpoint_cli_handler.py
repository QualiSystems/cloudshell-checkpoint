#!/usr/bin/python
# -*- coding: utf-8 -*-


from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.telnet_session import TelnetSession
from cloudshell.devices.cli_handler_impl import CliHandlerImpl

from cloudshell.checkpoint.gaia.cli.checkpoint_command_modes import MaintenanceCommandMode, EnableCommandMode, ExpertCommandMode
from cloudshell.checkpoint.gaia.sessions.console_ssh_session import ConsoleSSHSession
from cloudshell.checkpoint.gaia.sessions.console_telnet_session import ConsoleTelnetSession


class CheckpointCliHandler(CliHandlerImpl):
    def __init__(self, cli, resource_config, logger, api):
        super(CheckpointCliHandler, self).__init__(cli, resource_config, logger, api)
        self.modes = CommandModeHelper.create_command_mode(resource_config, api)

    @property
    def default_mode(self):
        return self.modes[MaintenanceCommandMode]

    @property
    def enable_mode(self):
        return self.modes[EnableCommandMode]

    @property
    def config_mode(self):
        return self.modes[ExpertCommandMode]

    def _console_ssh_session(self):
        console_port = int(self.resource_config.console_port)
        session = ConsoleSSHSession(self.resource_config.console_server_ip_address,
                                    self.username,
                                    self.password,
                                    console_port,
                                    self.on_session_start)
        return session

    def _console_telnet_session(self):
        console_port = int(self.resource_config.console_port)
        return [ConsoleTelnetSession(self.resource_config.console_server_ip_address,
                                     self.username,
                                     self.password,
                                     console_port,
                                     self.on_session_start),
                ConsoleTelnetSession(self.resource_config.console_server_ip_address,
                                     self.username,
                                     self.password,
                                     console_port,
                                     self.on_session_start,
                                     start_with_new_line=True)
                ]

    def _new_sessions(self):
        if self.cli_type.lower() == SSHSession.SESSION_TYPE.lower():
            new_sessions = self._ssh_session()
        elif self.cli_type.lower() == TelnetSession.SESSION_TYPE.lower():
            new_sessions = self._telnet_session()
        elif self.cli_type.lower() == "console":
            new_sessions = list()
            new_sessions.append(self._console_ssh_session())
            new_sessions.extend(self._console_telnet_session())
        else:
            new_sessions = [self._ssh_session(), self._telnet_session(),
                            self._console_ssh_session()]
            new_sessions.extend(self._console_telnet_session())
        return new_sessions

    def on_session_start(self, session, logger):
        """Send default commands to configure/clear session outputs
        :return:
        """

        session.send_line("set clienv rows 0", logger)
