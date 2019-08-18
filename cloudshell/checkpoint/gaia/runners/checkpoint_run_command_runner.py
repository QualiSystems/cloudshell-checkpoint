#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.runners.run_command_runner import RunCommandRunner


class CheckpointRunCommandRunner(RunCommandRunner):
    def __init__(self, cli_handler, logger):
        """Create CiscoRunCommandOperations

        :param CheckpointCliHandler cli_handler: Cli object
        :param qs_logger logger: logger
        :return:
        """

        super(CheckpointRunCommandRunner, self).__init__(logger, cli_handler)
