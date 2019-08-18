#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.runners.configuration_runner import ConfigurationRunner

from cloudshell.checkpoint.gaia.flows.checkpoint_restore_flow import CheckpointRestoreFlow
from cloudshell.checkpoint.gaia.flows.checkpoint_save_flow import CheckpointSaveFlow


class CheckpointConfigurationRunner(ConfigurationRunner):
    def __init__(self, cli_handler, logger, resource_config, api):
        """

        :param CheckpointCliHandler cli_handler: Cli object
        :param qs_logger logger: logger
        :param CloudShellAPISession api: cloudshell api object
        :param GenericNetworkingResource resource_config:
        """
        super(CheckpointConfigurationRunner, self).__init__(logger, resource_config, api, cli_handler)

    @property
    def restore_flow(self):
        return CheckpointRestoreFlow(cli_handler=self.cli_handler, logger=self._logger)

    @property
    def save_flow(self):
        return CheckpointSaveFlow(cli_handler=self.cli_handler, logger=self._logger)

    @property
    def file_system(self):
        return "flash:"
