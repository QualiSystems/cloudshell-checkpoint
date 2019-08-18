#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.runners.autoload_runner import AutoloadRunner
from cloudshell.checkpoint.gaia.flows.checkpoint_autoload_flow import CheckpointSnmpAutoloadFlow


class CheckpointAutoloadRunner(AutoloadRunner):
    def __init__(self, snmp_handler, logger, resource_config):
        super(CheckpointAutoloadRunner, self).__init__(resource_config)
        self.snmp_handler = snmp_handler
        self._logger = logger

    @property
    def autoload_flow(self):
        return CheckpointSnmpAutoloadFlow(self.snmp_handler, self._logger)
