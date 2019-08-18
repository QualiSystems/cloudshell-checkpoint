#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import OrderedDict

from cloudshell.devices.flows.action_flows import RestoreConfigurationFlow


class CheckpointRestoreFlow(RestoreConfigurationFlow):

    def __init__(self, cli_handler, logger):
        super(CheckpointRestoreFlow, self).__init__(cli_handler, logger)

    def execute_flow(self, path, configuration_type, restore_method, vrf_management_name):
        """ Execute flow which save selected file to the provided destination

        :param path: the path to the configuration file, including the configuration file name
        :param restore_method: the restore method to use when restoring the configuration file.
                               Possible Values are append and override
        :param configuration_type: the configuration type to restore. Possible values are startup and running
        :param vrf_management_name: Virtual Routing and Forwarding Name
        """

        pass
