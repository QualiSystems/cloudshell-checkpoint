#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.runners.state_runner import StateRunner


class CheckpointStateRunner(StateRunner):
    def __init__(self, cli_handler, logger, api, resource_config):
        """

        :param CheckpointCliHandler cli_handler: Cli object
        :param qs_logger logger: logger
        :param CloudShellAPISession api: cloudshell api object
        :param GenericNetworkingResource resource_config:
        """

        super(CheckpointStateRunner, self).__init__(logger, api, resource_config, cli_handler)
        self.api = api
