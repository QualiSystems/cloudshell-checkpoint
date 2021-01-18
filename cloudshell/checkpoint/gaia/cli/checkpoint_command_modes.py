#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import random
from collections import OrderedDict

from backports.functools_lru_cache import lru_cache
from passlib.hash import md5_crypt

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
            enter_error_map={r"[Ww]rong\spassword": "Wrong password."},
            enter_action_map={
                "[Pp]assword":
                    lambda session, logger: (session.send_line(self.enable_password, logger),
                                             session.send_line('\n', logger)),
                # Raise an error action
                r"[Ww]rong\spassword": lambda s, l: self._exception("Incorrect expert password.")
            }
        )

    @staticmethod
    def _exception(message):
        raise Exception(message)

    def _expert_password_defined(self, cli_service, logger):
        """
        Check if expert password defined
        :param cloudshell.cli.cli_service_impl.CliServiceImpl cli_service:
        :param logging.Logger logger:
        :rtype: bool
        """
        logger.debug("Check if expert password defined.")
        if isinstance(cli_service.command_mode, EnableCommandMode):
            result = cli_service.send_command("show configuration expert-password")
            return re.match(r'^set\sexpert-password-hash\s.+$', result, re.MULTILINE) is not None
        else:
            raise Exception("Cannot verify expert password, command mode is not correct")

    def _set_expert_password(self, cli_service, logger):
        """
        Set expert password
        :param cloudshell.cli.cli_service.CliService cli_service:
        :param logging.Logger logger:
        :rtype: bool
        """

        # gen enable password hash
        enable_password_hash = md5_crypt.hash(self.enable_password, salt_size=random.choice(range(5, 8)))

        error_map = OrderedDict([("Configuration lock present", "Configuration lock present."),
                                 ("Failed to maintain the lock", "Failed to maintain the lock."),
                                 ("Wrong password", "Wrong password.")])
        cli_service.send_command(command="set expert-password-hash {}".format(enable_password_hash),
                                 logger=logger,
                                 error_map=error_map)

    def step_up(self, cli_service, logger):
        if not self._expert_password_defined(cli_service, logger):
            self._set_expert_password(cli_service, logger)
        super(ExpertCommandMode, self).step_up(cli_service, logger)

    @property
    @lru_cache()
    def enable_password(self):
        return self._api.DecryptPassword(self.resource_config.enable_password).Value


CommandMode.RELATIONS_DICT = {
    MaintenanceCommandMode: {
        EnableCommandMode: {
            ExpertCommandMode: {}
        }
    }
}
