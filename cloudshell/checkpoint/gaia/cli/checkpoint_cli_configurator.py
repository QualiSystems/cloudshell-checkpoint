#!/usr/bin/python
# -*- coding: utf-8 -*-
from collections import OrderedDict
from functools import lru_cache

from cloudshell.cli.service.command_mode_helper import CommandModeHelper

from cloudshell.cli.configurator import AbstractModeConfigurator

from cloudshell.checkpoint.gaia.cli.checkpoint_command_modes import MaintenanceCommandMode, EnableCommandMode, \
    ExpertCommandMode
from cloudshell.checkpoint.gaia.cli.sessions.console_ssh_session import ConsoleSSHSession
from cloudshell.checkpoint.gaia.cli.sessions.console_telnet_session import ConsoleTelnetSession


class CheckpointCliConfigurator(AbstractModeConfigurator):
    def __init__(self, cli, resource_config, logger):
        """
        :param cloudshell.cli.service.cli.CLI cli:
        :param cloudshell.shell.standards.firewall.resource_config.FirewallResourceConfig resource_config:
        :param logging.logger logger:
        """
        super(CheckpointCliConfigurator, self).__init__(resource_config, logger, cli)
        self.modes = CommandModeHelper.create_command_mode(resource_config)

    @property
    def default_mode(self):
        return self.modes[MaintenanceCommandMode]

    @property
    def enable_mode(self):
        return self.modes[EnableCommandMode]

    @property
    def config_mode(self):
        return self.modes[ExpertCommandMode]

    def _console_ssh_session(self, **kwargs):
        console_port = int(self.resource_config.console_port)
        session = ConsoleSSHSession(self.resource_config.console_server_ip_address,
                                    self.username,
                                    self.password,
                                    console_port,
                                    self.on_session_start)
        return session

    def _console_telnet_session(self, **kwargs):
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

    # def _new_sessions(self):
    #     if self.cli_type.lower() == SSHSession.SESSION_TYPE.lower():
    #         new_sessions = self._ssh_session()
    #     elif self.cli_type.lower() == TelnetSession.SESSION_TYPE.lower():
    #         new_sessions = self._telnet_session()
    #     elif self.cli_type.lower() == "console":
    #         new_sessions = list()
    #         new_sessions.append(self._console_ssh_session())
    #         new_sessions.extend(self._console_telnet_session())
    #     else:
    #         new_sessions = [self._ssh_session(), self._telnet_session(),
    #                         self._console_ssh_session()]
    #         new_sessions.extend(self._console_telnet_session())
    #     return new_sessions

    @property
    @lru_cache()
    def _session_dict(self):
        return OrderedDict(super(CheckpointCliConfigurator, self)._session_dict.items()+[(
            "console", [self._console_ssh_session, self._console_telnet_session])])

    def _on_session_start(self, session, logger):
        """Send default commands to configure/clear session outputs
        :return:
        """

        session.send_line("set clienv rows 0", logger)
