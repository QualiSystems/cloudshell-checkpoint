#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.runners.firmware_runner import FirmwareRunner

from cloudshell.checkpoint.gaia.cli.checkpoint_cli_handler import CheckpointCliHandler
from cloudshell.checkpoint.gaia.flows.checkpoint_load_firmware_flow import CheckpointLoadFirmwareFlow


class CheckpointFirmwareRunner(FirmwareRunner):
    RELOAD_TIMEOUT = 500

    def __init__(self, cli_handler, logger):
        """Handle firmware upgrade process

        :param CheckpointCliHandler cli_handler: Cli object
        :param qs_logger logger: logger
        """

        super(CheckpointFirmwareRunner, self).__init__(logger, cli_handler)

    @property
    def load_firmware_flow(self):
        return CheckpointLoadFirmwareFlow(self.cli_handler, self._logger)
