#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.snmp_handler import SnmpHandler
from cloudshell.checkpoint.gaia.cli.checkpoint_cli_handler import CheckpointCliHandler
from cloudshell.checkpoint.gaia.flows.checkpoint_disable_snmp_flow import CheckpointDisableSnmpFlow
from cloudshell.checkpoint.gaia.flows.checkpoint_enable_snmp_flow import CheckpointEnableSnmpFlow


class CheckpointSnmpHandler(SnmpHandler):
    def __init__(self, cli, resource_config, logger, api):
        super(CheckpointSnmpHandler, self).__init__(resource_config, logger, api)
        self._cli = cli
        self._api = api

    @property
    def cli_handler(self):
        return CheckpointCliHandler(self._cli, self.resource_config, self._logger, self._api)

    def _create_enable_flow(self):
        return CheckpointEnableSnmpFlow(self.cli_handler, self._logger)

    def _create_disable_flow(self):
        return CheckpointDisableSnmpFlow(self.cli_handler, self._logger)
