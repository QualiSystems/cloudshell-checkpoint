#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.cli.command_mode import CommandMode


class MaintenanceCommandMode(CommandMode):
    PROMPT = r'(?:(?!\)).)#\s*$'  # TODO Verify prompt correctness
    ENTER_COMMAND = ''
    EXIT_COMMAND = ''

    def __init__(self, resource_config, api):
        """ Initialize Default command mode, only for cases when session started not in enable mode """

        self.resource_config = resource_config
        self._api = api

        CommandMode.__init__(self,
                             MaintenanceCommandMode.PROMPT,
                             MaintenanceCommandMode.ENTER_COMMAND,
                             MaintenanceCommandMode.EXIT_COMMAND)

        super(MaintenanceCommandMode, self).__init__(
            self.PROMPT,
            self.ENTER_COMMAND,
            self.EXIT_COMMAND
        )


class EnableCommandMode(CommandMode):
    PROMPT = r'>\s*$'
    ENTER_COMMAND = 'clish'
    EXIT_COMMAND = ''

    def __init__(self, resource_config, api):
        """ Initialize Enable command mode - default command mode for CheckPoint Shells """

        self.resource_config = resource_config
        self._api = api

        super(EnableCommandMode, self).__init__(
            self.PROMPT,
            self.ENTER_COMMAND,
            self.EXIT_COMMAND
        )


class ExpertCommandMode(CommandMode):
    PROMPT = r'\[Expert.*#\s*$'
    ENTER_COMMAND = 'expert'
    EXIT_COMMAND = 'exit'

    def __init__(self, resource_config, api):
        """ Initialize Expert Command Mode """

        self.resource_config = resource_config
        self._api = api
        self._enable_password = None

        CommandMode.__init__(self,
                             ExpertCommandMode.PROMPT,
                             ExpertCommandMode.ENTER_COMMAND,
                             ExpertCommandMode.EXIT_COMMAND)

        super(ExpertCommandMode, self).__init__(
            self.PROMPT,
            self.ENTER_COMMAND,
            self.EXIT_COMMAND,
            enter_action_map={
                "[Pp]assword":
                    lambda session, logger: (session.send_line(self.enable_password, logger),
                                             session.send_line("clear", logger))
            }
        )

    @property
    def enable_password(self):
        if not self._enable_password:
            password = self.resource_config.enable_password
            self._enable_password = self._api.DecryptPassword(password).Value
        return self._enable_password


CommandMode.RELATIONS_DICT = {
    MaintenanceCommandMode: {
        EnableCommandMode: {
            ExpertCommandMode: {}
        }
    }
}
